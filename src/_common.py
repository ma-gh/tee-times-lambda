from collections import namedtuple
from typing import List

from tee_time_checkers.driver import COURSE_CHECKERS


class InputError(Exception):
    pass


class UnknownCourseError(InputError):
    pass


InputTuple = namedtuple("InputTuple", "earliest_time latest_time days_ahead courses")


def validate_courses(courses: List[str]):
    for course in courses:
        if course not in COURSE_CHECKERS.keys():
            raise UnknownCourseError(course)
    return courses
