from tee_time_checkers.foreup_checker import ForeupTeeTimeChecker, ForeupUrl


class MileSquarePlayersTeeTimeChecker(ForeupTeeTimeChecker):
    def get_foreup_url(self):
        return ForeupUrl(booking_class="3414", schedule_id="3760")


if __name__ == "__main__":
    print(MileSquarePlayersTeeTimeChecker().find_ok_tee_times())
