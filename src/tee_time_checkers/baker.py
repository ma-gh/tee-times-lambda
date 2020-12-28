import json
from datetime import datetime
from typing import List

import requests

from tee_time_checkers.base_checker import TeeTimeChecker

URL = "https://davidlbakerpp.ezlinksgolf.com/api/search/search"
API_DATE_FORMAT = r"%m/%d/%Y"
API_REQUEST_DATA = {
    "numHoles": 1,  # Means 18 holes
    "numPlayers": 2,
    "startTime": "5:00 AM",
    "endTime": "7:00 PM",
    "courseIDs": [2939],
    "holdAndReturnOne": False,
}


class BakerTeeTimeChecker(TeeTimeChecker):
    def _get_tee_times(self, dt: datetime) -> List[str]:
        data = API_REQUEST_DATA.copy()
        data["date"] = datetime.strftime(dt, API_DATE_FORMAT)
        data = json.loads(requests.post(URL, data=data).text).get("Reservations", [])
        raw_times = filter(bool, map(lambda item: item.get("TeeTime"), data))
        return list(raw_times)


if __name__ == "__main__":
    BakerTeeTimeChecker().find_ok_tee_times()
