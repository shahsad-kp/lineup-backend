from Calender.models import CalendarAccount


class CalendarAlreadyExistsError(Exception):
    def __init__(self, existing_calendar: CalendarAccount, *args):
        self.existing_calendar = existing_calendar
        super().__init__(*args)
