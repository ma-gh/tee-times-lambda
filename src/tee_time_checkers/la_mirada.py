import json
from datetime import datetime
from typing import List

import requests

from tee_time_checkers.base_checker import TeeTimeChecker

URL = (
    "https://foreupsoftware.com/index.php/api/booking/times"
    "?time=all"
    "&date={}"
    "&holes=18"
    "&players=2"
    "&booking_class=3969"
    "&schedule_id=4474"
    "&schedule_ids%5B%5D=0,4474"
    "&specials_only=0"
    "&api_key=no_limits"
)
API_DATE_FORMAT = r"%m-%d-%Y"


class LaMiradaTeeTimeChecker(TeeTimeChecker):
    def _get_tee_times(self, dt: datetime) -> List[str]:
        date_string = datetime.strftime(dt, API_DATE_FORMAT)
        data = json.loads(requests.get(URL.format(date_string)).text)
        raw_times = map(lambda item: item.get("time", "ERROR"), data)
        return list(raw_times)
