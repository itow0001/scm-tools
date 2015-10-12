'''
Created on Oct 8, 2015

@author: iitow
'''
import sys,time,calendar
from datetime import datetime,date
from calendar import timegm
sys.path.append('../lib')
from github_kit import Github
def time_delta(timestamp):
    """ Give me the delta time UTC of a last commit from ghost user"""
    timestamp = timegm(time.strptime(timestamp.replace('Z', 'GMT'),'%Y-%m-%dT%H:%M:%S%Z'))
    timestamp = datetime.utcfromtimestamp(timestamp)
    present = datetime.utcnow()
    delta = present - timestamp
    print "  timestamp: %s" % timestamp
    print "    present: %s" % present
    print "      delta: %s" % delta
    return delta
def has_failed(delta):
    """Determines if ghosts commit is more then 24hrs old and not a weekend """
    week_day = calendar.day_name[date.today().weekday()]
    days = delta.days
    hrs  = delta.seconds/3600
    print "current day: %s" % week_day
    print " delta days: %s" % days
    print "  delta hrs: %s" % hrs
    if (week_day == "Saturday" or week_day == "Sunday"):
        return False
    elif days <1:
            return False
    return True
if __name__ == '__main__':
    base_url = "github.west.isilon.com"
    auth_file= "../auth/github.json"
    g1 = Github(base_url,auth_file)
    message = g1.get('users/ghost/events/public?page=0&per_page=1')[0]
    fail = has_failed(time_delta(message.get("created_at")))
    print "svn2git has failed: %s" % (fail)
    if fail == True:
        sys.exit(1)