import json
import os
import traceback
from collections import namedtuple
from http import HTTPStatus
from typing import List

import boto3
import botocore

from tee_time_checkers.driver import COURSE_CHECKERS, run

InputTuple = namedtuple("InputTuple", "earliest_time latest_time days_ahead courses")


class InputError(Exception):
    pass


class UnknownCourseError(InputError):
    pass


def _parse_event(event) -> InputTuple:
    try:
        return InputTuple(
            earliest_time=event["earliestTime"],
            latest_time=event["latestTime"],
            days_ahead=event.get("daysAhead"),
            courses=event["courses"],
        )
    except KeyError as err:
        raise InputError() from err


def _validate_courses(courses: List[str]):
    for course in courses:
        if course not in COURSE_CHECKERS.keys():
            raise UnknownCourseError(course)
    return courses


def get_courses(event=None, context=None):
    return list(COURSE_CHECKERS.keys())


def get_tee_times(event=None, context=None):
    print(f"Triggered for event: {event}")
    try:
        earliest_time, latest_time, days_ahead, courses = _parse_event(event)
        _validate_courses(courses)
        response = run(courses, earliest_time, latest_time, days_ahead)
        return {"statusCode": HTTPStatus.OK, "body": json.dumps(response)}
    except InputError as err:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": repr(err)}
    except Exception as e:
        traceback.print_exc()
        return {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR, "body": repr(err)}


def _parse_env_vars() -> InputTuple:
    try:
        return InputTuple(
            earliest_time=os.environ["EARLIEST_TIME"],
            latest_time=os.environ["LATEST_TIME"],
            days_ahead=os.environ.get("DAYS_AHEAD"),
            courses=os.environ["COURSES"].split(","),
        )
    except KeyError as err:
        raise InputError() from err


def _format_tee_times(response) -> List[str]:
    """Flatten the response dict into a single list to easily compare."""
    return [
        f"{course_name} @ {tee_time}"
        for course_name, tee_times in response.items()
        for tee_time in tee_times
    ]


def _get_diff(prev, curr):
    prev, curr = set(prev), set(curr)
    added = sorted(list(curr.difference(prev)))
    removed = sorted(list(prev.difference(curr)))
    return added, removed


def notify_tee_times(event=None, context=None):
    earliest_time, latest_time, days_ahead, courses = _parse_env_vars()
    _validate_courses(courses)

    if response := run(courses, earliest_time, latest_time, days_ahead):
        formatted_tee_times = _format_tee_times(response)
        print(f"Current tee times found: {formatted_tee_times}")

        s3 = boto3.resource("s3")
        bucket_name = key = os.environ["NOTIFY_TEE_TIMES_BUCKET_NAME"]  # Key doesn't matter
        obj = s3.Object(bucket_name, key)
        prev = []
        try:
            prev = json.loads(obj.get()["Body"].read().decode("utf-8"))
            print(f"Previous tee times found: {prev}")
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Code"] == "NoSuchKey":
                # Object doesn't exist
                pass
            else:
                raise

        added, removed = _get_diff(prev, formatted_tee_times)
        print(f"{added=}, {removed=}")

        obj.put(Body=json.dumps(formatted_tee_times))

        # Post message
        message = ""
        if added:
            message += f"Newly available tee times:\n{json.dumps(added, indent=4)}\n"
        if removed:
            message += f"No longer available tee times:\n{json.dumps(removed, indent=4)}\n"
        sns = boto3.client("sns")
        sns.publish(
            TopicArn=os.environ["OUTPUT_TOPIC_ARN"],
            Subject=f"Found {len(formatted_tee_times)} total available tee times.",
            Message=message,
        )
        print("Published message successfully")
