from tee_time_checkers.foreup_checker import ForeupTeeTimeChecker, ForeupUrl


class MileSquareClassicTeeTimeChecker(ForeupTeeTimeChecker):
    def get_foreup_url(self):
        return ForeupUrl(booking_class="3413", schedule_id="3759")


if __name__ == "__main__":
    print(MileSquareClassicTeeTimeChecker().find_ok_tee_times())
