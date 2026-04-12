from icalendar import Calendar
import caldav
import keys


def retrieve_calendar_events():
    '''
    Obtain the calendar from the user and get events
    '''
    url = f'https://www.google.com/calendar/dav/{keys.EMAIL_USER}/user'
    client = caldav.DAVClient(
        url=url,
        username=keys.EMAIL_USER,
        password=keys.CALENDAR_PASSWORD,
    )
    principal = client.principal()
    calendar = principal.calendar(name=keys.CALENDAR)

    all_events = []

    for event in calendar.events():
        cal = Calendar.from_ical(event.data)
        for component in cal.walk("VEVENT"):
            summary = component.get("summary", "No title")
            start = component.get("dtstart").dt

            attendees = component.get('attendee')
            if not isinstance(attendees, list):
                # In case there's a single attendee
                attendees = [attendees]

            attendees = [att.params.get('CN') for att in attendees]
            event = {
                'start': start,
                'summary': str(summary),
                'attendees': attendees,
            }

            all_events.append(event)

    return all_events


if __name__ == '__main__':
    events = retrieve_calendar_events()
    print(events)
