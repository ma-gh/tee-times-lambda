import json
from datetime import datetime
from typing import List

import requests

from tee_time_checkers.base_checker import TeeTimeChecker

URL = "https://westridge.ezlinksgolf.com/api/search/search"
API_DATE_FORMAT = r"%m/%d/%Y"
API_REQUEST_DATA = {
    "p06": 2,  # Players
    "p02": "",  # Date
    "p03": "5:00 AM",  # Start time
    "p04": "7:00 PM",  # End time
    "p05": 0,
    "p01": [19844],  # Course IDs
    "p07": False,  # holdAndReturnOne
}


class WestridgeTeeTimeChecker(TeeTimeChecker):
    def _get_tee_times(self, dt: datetime) -> List[str]:
        data = API_REQUEST_DATA.copy()
        data["p02"] = datetime.strftime(dt, API_DATE_FORMAT)
        data = json.loads(requests.post(URL, data=data).text).get("r06", [])
        raw_times = filter(bool, map(lambda item: item.get("r15"), data))
        return list(raw_times)


if __name__ == "__main__":
    print(WestridgeTeeTimeChecker().find_ok_tee_times())
