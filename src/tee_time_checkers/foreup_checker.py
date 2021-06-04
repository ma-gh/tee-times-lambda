import json
from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests

from tee_time_checkers.base_checker import TeeTimeChecker


@dataclass
class ForeupUrl:
    url_template = (
        "https://foreupsoftware.com/index.php/api/booking/times"
        "?time=all"
        "&date={}"
        "&holes=18"
        "&players=2"
        "&specials_only=0"
        "&api_key=no_limits"
    )
    api_date_format = r"%m-%d-%Y"

    booking_class: str
    schedule_id: str

    def create(self, dt: datetime):
        url_template = (
            self.url_template
            + f"&booking_class={self.booking_class}"
            + f"&schedule_id={self.schedule_id}"
        )
        date_string = datetime.strftime(dt, self.api_date_format)
        return url_template.format(date_string)


class ForeupTeeTimeChecker(TeeTimeChecker):
    def _get_tee_times(self, dt: datetime) -> List[str]:
        data = json.loads(requests.get(self.get_foreup_url().create(dt)).text)
        raw_times = map(lambda item: item.get("time", "ERROR"), data)
        return list(raw_times)

    @abstractmethod
    def get_foreup_url(self) -> ForeupUrl:
        pass
