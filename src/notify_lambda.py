import json
import os
from typing import List

import boto3
import botocore

from _common import InputError, InputTuple, validate_courses
from tee_time_checkers.driver import run

NOTIFY_TEE_TIMES_BUCKET_NAME = os.environ["NOTIFY_TEE_TIMES_BUCKET_NAME"]
OUTPUT_TOPIC_ARN = os.environ["OUTPUT_TOPIC_ARN"]

S3_OBJ = boto3.resource("s3").Object(NOTIFY_TEE_TIMES_BUCKET_NAME, "notify-tee-times-object")
SNS = boto3.client("sns")


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


def _get_prev_tee_times():
    try:
        return json.loads(S3_OBJ.get()["Body"].read().decode("utf-8"))
    except botocore.exceptions.ClientError as err:
        if err.response["Error"]["Code"] == "NoSuchKey":
            # Object doesn't exist
            return []
        else:
            raise


def _get_diff(prev, curr):
    prev, curr = set(prev), set(curr)
    added = sorted(list(curr.difference(prev)))
    removed = sorted(list(prev.difference(curr)))
    return added, removed


def _put_new_tee_times(curr_tee_times):
    S3_OBJ.put(Body=json.dumps(curr_tee_times))


def _format_message(added, removed):
    subject = f"Tee Times Alert: {len(added)} added, {len(removed)} removed"
    message = ""
    if added:
        message += f"Newly available:\n{json.dumps(added, indent=4)}\n"
    if removed:
        message += f"No longer available:\n{json.dumps(removed, indent=4)}\n"
    message += "https://foreupsoftware.com/index.php/booking/20096/3759#teetimes"
    return subject, message


def notify_tee_times(event=None, context=None):
    earliest_time, latest_time, days_ahead, courses = _parse_env_vars()
    validate_courses(courses)

    if response := run(courses, earliest_time, latest_time, days_ahead):
        curr_tee_times = _format_tee_times(response)
        print(f"Current tee times found: {curr_tee_times}")

        prev_tee_times = _get_prev_tee_times()
        print(f"Prev tee times found: {prev_tee_times}")

        added, removed = _get_diff(prev_tee_times, curr_tee_times)
        print(f"{added=}, {removed=}")

        _put_new_tee_times(curr_tee_times)

        subject, message = _format_message(added, removed)
        SNS.publish(TopicArn=OUTPUT_TOPIC_ARN, Subject=subject, Message=message)
        print("Published message successfully")
