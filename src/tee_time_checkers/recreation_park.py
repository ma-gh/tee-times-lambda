from tee_time_checkers.foreup_checker import ForeupTeeTimeChecker, ForeupUrl


class RecreationParkTeeTimeChecker(ForeupTeeTimeChecker):
    def get_foreup_url(self):
        return ForeupUrl(booking_class="3474", schedule_id="3927")


if __name__ == "__main__":
    print(RecreationParkTeeTimeChecker().find_ok_tee_times())
