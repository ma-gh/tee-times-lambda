import json
import traceback
from collections import namedtuple
from http import HTTPStatus
from typing import List

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
