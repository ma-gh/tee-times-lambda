from tee_time_checkers.foreup_checker import ForeupTeeTimeChecker, ForeupUrl


class LaMiradaTeeTimeChecker(ForeupTeeTimeChecker):
    def get_foreup_url(self):
        return ForeupUrl(booking_class="3969", schedule_id="4474")


if __name__ == "__main__":
    print(LaMiradaTeeTimeChecker().find_ok_tee_times())
