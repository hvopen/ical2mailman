#!/usr/bin/env python

# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import icalendar
import re
import robobrowser
import time
import urllib2
import yaml


def next_meetings(count=3):
    """Find the next N meetings from our ical.

    After getting the ical, run through it looking for Events,
    which are in the future, and include 'meetings' in the url,
    which means they are Drupal meeting types, and not other
    kinds of events like Lunch or Conferences.

    Because we know that July (7) and August (8) we'll be at
    Lourdes, add an annotation to the events in those months. People
    seem to use the email footer for more info than I'd expect so
    hopefully this means less people getting lost.
    """
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
            if dt.month == 7:
                meeting += " @ Lourdes"
            meetings.append(meeting)
            found += 1
    return meetings


def update_mailman(meetings, passwd=""):
    """Log into mailman and update the footer with meetings.

    Using python mechanize log into the mailman admin interface, strip
    off the end of the footer and replace it with the updated list of meetings.
    The text for this is hardcoded based on our needs, but it's at least
    a pretty good example of how to do it.
    """
    br = robobrowser.RoboBrowser()
    br.open("https://mhvlug.org/cgi-bin/mailman/admin/mhvlug/nondigest")
    form = br.get_form(action='/cgi-bin/mailman/admin/mhvlug/nondigest')
    form['adminpw'].value = passwd
    br.submit_form(form)

    # Now we are logged in
    br.open("https://mhvlug.org/cgi-bin/mailman/admin/mhvlug/nondigest")
    form = br.get_forms()[0]
    cur_footer = form['msg_footer'].value.split("Upcoming Meetings")[0]
    cur_footer += ("Upcoming Meetings (6pm - 8pm)                         "
                   "Vassar College *\n")
    for meeting in meetings:
        cur_footer += meeting + "\n"
    form['msg_footer'].value = cur_footer

    br.submit_form(form)


def load_conf():
    return yaml.load(open("config.yaml"))


def main():
    conf = load_conf()
    meetings = next_meetings(int(conf['entries']))
    update_mailman(meetings, passwd=conf['pass'])


if __name__ == '__main__':
    main()
