#!/usr/bin/env python

import datetime
import icalendar
import mechanize
import re
import time
import urllib2
import yaml


def next_meetings(count=3):
    f = urllib2.urlopen("https://mhvlug.org/calendar/ical")
    ical = f.read()
    cal = icalendar.Calendar()
    cal = cal.from_ical(ical)
    now = datetime.datetime.now()
    found = 0
    meetings = []
    for event in cal.subcomponents:
        if found >= count:
            break
        if type(event) != icalendar.cal.Event:
            continue
        # oh time...
        dt = event['DTSTART'].dt
        then = datetime.datetime.fromtimestamp(time.mktime(dt.utctimetuple()))
        if then < now:
            continue
        if re.search('meetings', event['URL']):
            meeting = ("  %s - %s" % (
                dt.strftime("%b %e"), event['SUMMARY'].title()))
            if dt.month == 7 or dt.month == 8:
                meeting += " @ Lourdes"
            meetings.append(meeting)
            found += 1
    return meetings


def update_mailman(meetings, passwd=""):
    br = mechanize.Browser()
    br.open("https://mhvlug.org/cgi-bin/mailman/admin/mhvlug/nondigest")
    br.select_form(name='f')
    br['adminpw'] = passwd
    br.submit()

    # Now we are logged in
    br.open("https://mhvlug.org/cgi-bin/mailman/admin/mhvlug/nondigest")
    br.select_form(nr=0)
    cur_footer = br['msg_footer'].split("Upcoming Meetings")[0]
    cur_footer += ("Upcoming Meetings (6pm - 8pm)                         "
                   "Vassar College *\n")
    for meeting in meetings:
        cur_footer += meeting + "\n"
    br['msg_footer'] = cur_footer
    br.submit()


def load_conf():
    return yaml.load(open("config.yaml"))


def main():
    conf = load_conf()
    meetings = next_meetings()
    update_mailman(meetings, passwd=conf['pass'])


if __name__ == '__main__':
    main()
