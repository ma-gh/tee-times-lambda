import json
import traceback
from http import HTTPStatus

from _common import InputError, InputTuple, validate_courses
from tee_time_checkers.driver import COURSE_CHECKERS, run


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


def get_courses(event=None, context=None):
    return list(COURSE_CHECKERS.keys())


def get_tee_times(event=None, context=None):
    print(f"Triggered for event: {event}")
    try:
        earliest_time, latest_time, days_ahead, courses = _parse_event(event)
        validate_courses(courses)
        response = run(courses, earliest_time, latest_time, days_ahead)
        return {"statusCode": HTTPStatus.OK, "body": json.dumps(response)}
    except InputError as err:
        return {"statusCode": HTTPStatus.BAD_REQUEST, "body": repr(err)}
    except Exception as err:
        traceback.print_exc()
        return {"statusCode": HTTPStatus.INTERNAL_SERVER_ERROR, "body": repr(err)}
