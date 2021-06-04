from collections import defaultdict
from queue import Queue
from threading import Thread
from typing import Dict, List

from tee_time_checkers.baker import BakerTeeTimeChecker
from tee_time_checkers.la_mirada import LaMiradaTeeTimeChecker
from tee_time_checkers.mile_square_classic import MileSquareClassicTeeTimeChecker
from tee_time_checkers.mile_square_players import MileSquarePlayersTeeTimeChecker
from tee_time_checkers.recreation_park import RecreationParkTeeTimeChecker
from tee_time_checkers.skylinks import SkylinksTeeTimeChecker
from tee_time_checkers.westridge import WestridgeTeeTimeChecker

COURSE_CHECKERS = {
    "Mile Square Players Course": MileSquarePlayersTeeTimeChecker,
    "Mile Square Classic Course": MileSquareClassicTeeTimeChecker,
    "Baker": BakerTeeTimeChecker,
    "La Mirada": LaMiradaTeeTimeChecker,
    "Recreation Park": RecreationParkTeeTimeChecker,
    "Skylinks": SkylinksTeeTimeChecker,
    "Westridge": WestridgeTeeTimeChecker,
}


def run(courses: List[str], *args) -> Dict:
    queue = Queue(len(courses) * 2)
    response = defaultdict(dict)

    # Consumer
    def consumer():
        course = queue.get()
        checker = COURSE_CHECKERS[course](*args)
        response[course] = checker.find_ok_tee_times()
        queue.task_done()

    # Create threads
    for _ in range(len(courses)):
        t = Thread(target=consumer)
        t.daemon = True
        t.start()

    # Enqueue requests
    for course in courses:
        queue.put(course)

    # Wait for all threads to finish
    queue.join()

    return response
