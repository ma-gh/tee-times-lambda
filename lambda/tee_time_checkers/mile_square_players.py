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
    "&booking_class=3414"
    "&schedule_id=3760"
    "&schedule_ids%5B%5D=0"
    "&schedule_ids%5B%5D=3759"
    "&schedule_ids%5B%5D=3760"
    "&specials_only=0"
    "&api_key=no_limits"
)
API_DATE_FORMAT = r"%m-%d-%Y"


class MileSquarePlayersTeeTimeChecker(TeeTimeChecker):
    def _get_tee_times(self, dt: datetime) -> List[str]:
        date_string = datetime.strftime(dt, API_DATE_FORMAT)
        data = json.loads(requests.get(URL.format(date_string)).text)
        raw_times = map(lambda item: item.get("time", "ERROR"), data)
        return list(raw_times)


if __name__ == "__main__":
    MileSquarePlayersTeeTimeChecker().find_ok_tee_times()
