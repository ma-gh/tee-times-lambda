import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from typing import List


class TeeTimeChecker(ABC):
    def __init__(self, earliest_time, latest_time, days_ahead):
        self.earliest_time = earliest_time
        self.latest_time = latest_time
        self.days_ahead = int(days_ahead) if days_ahead else 8

        self._queue = Queue(self.days_ahead * 2)
        self._results = []

    @abstractmethod
    def _get_tee_times(self, dt: datetime) -> List[str]:
        pass

    @staticmethod
    def _to_minutes(time_string) -> int:
        match = re.search(r"(\d{1,2}):(\d{2})", time_string)
        hours, minutes = int(match.group(1)), int(match.group(2))
        pm_offset = (12 * 60) if ("PM" in time_string.upper() and hours < 12) else 0
        return pm_offset + hours * 60 + minutes

    def _get_dates_ahead(self) -> List[datetime]:
        today = datetime.now()
        return [today + timedelta(days=i) for i in range(self.days_ahead)]

    def _is_ok_time(self, tee_time: str) -> bool:
        tee_time_minutes = TeeTimeChecker._to_minutes(tee_time)
        earliest_minutes = TeeTimeChecker._to_minutes(self.earliest_time)
        latest_minutes = TeeTimeChecker._to_minutes(self.latest_time)
        return earliest_minutes <= tee_time_minutes <= latest_minutes


    def _get_tee_times_concurrent(self):
        # Pull a request
        dt =  self._queue.get()

        # Work on the request
        result = self._get_tee_times(dt)

        # Append the result
        self._results += result
        self._queue.task_done()

    def _get_all_tee_times(self):
        dates = self._get_dates_ahead()

        # Create threads
        for _ in range(len(dates)):
            t = Thread(target=self._get_tee_times_concurrent)
            t.daemon = True
            t.start()

        # Enqueue requests
        for dt in dates:
            self._queue.put(dt)

        # Wait for threads to finish
        self._queue.join()

        # Return results
        return self._results

    def find_ok_tee_times(self) -> List[str]:
        return list(filter(self._is_ok_time, self._get_all_tee_times()))
