from tee_time_checkers.foreup_checker import ForeupTeeTimeChecker, ForeupUrl


class SkylinksTeeTimeChecker(ForeupTeeTimeChecker):
    def get_foreup_url(self):
        return ForeupUrl(booking_class="3501", schedule_id="3939")


if __name__ == "__main__":
    print(SkylinksTeeTimeChecker().find_ok_tee_times())
