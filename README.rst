==============
 ical2mailman
==============

This is a program used by mhvlug.org to synchronize our ical feed into
our mailman footer for all meetings getting sent out.

While not incredibly pretty code, it does provide a reasonable example
of both using the python icalendar parser, as well as using python's
mechanize to automatically update a site that doesn't have a
reasonable web api.

Suggestions or patches welcomed.

Installation
============

On an Ubuntu system:

 - sudo apt-get install python-mechanize python-icalendar python-yaml
 - cp config.yaml.sample config.yaml
 - set the mailman admin password in config.yaml
 - ./ical2mailman
