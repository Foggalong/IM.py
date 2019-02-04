#!/usr/bin/env python3

"""
@author  = Joshua Fogg
@license = GNU GPL v3+

This program tracks the connection status of NL IM services. It does
not track connection speeds, only whether it would be possible for a
visitor to begin a chat or not.
"""


from csv import reader                  # data stored in CSV files
from datetime import date               # date stamped data files
from filecmp import cmp                 # comparing status gifs
from os import makedirs, path           # verifying log directory
from sys import stdout                  # reuse output lines
from time import strftime, sleep        # time formats, timed execution
from urllib.request import urlretrieve  # download status gifs


# SERVICES DATA
# Loads the services data from a CSV file (Name, Status URL) into
# a dictionary file with service name as key, IM status URL as value

services = dict()
data = open("data/services.csv")
for entry in reader(data):
    services[entry[0]] = entry[1]
services.pop("Name")  # ditch header row
data.close()


# CHECK & LOG FUNCTIONS
# Functions involved in checking whether a service is currently
# online and then logging the results.

def logStatus(status):
    stdout.write(" IM " + status + "\n")
    log.write(currentTime + "," + status + "\n")


# Check status of a service
def statusCheck(log, service):
    stdout.write(str(service))
    # Trys to download the current status image
    try:
        url = services[service] + "/webim/b.php?i=mblue"
        urlretrieve(url, "status.gif")

        # Checks if status.gif matches either known images
        if cmp("status.gif", "data/offline.gif"):
            logStatus("offline")
        elif cmp("status.gif", "data/online.gif"):
            logStatus("online")
        else:
            logStatus("unknown")
            # TODO: raise exception? copy gif to error check

    # TODO: needs switching to specific exceptopm types
    except:
        logStatus("failed")
        # TODO: copy the status.gif that failed to somewhere to error check


# RUNNING TRACKER

while True:
    currentTime = strftime("%H:%M")
    print("Running at", currentTime)

    # Only interested in tracking status between 5pm and 9am
    hour = int(strftime("%H"))
    if hour not in range(9, 17):
        # Logfile name needs to be the date the shift *started*
        if hour in range(20, 24):
            logfile = str(date.today())
        elif hour in range(0, 9):
            logfile = str(date.fromordinal(date.today().toordinal()-1))

        # Perform status check for each service
        for service in services:
            # skip services which have no IM
            if not services[service].startswith("https://"):
                continue

            # if no data directory exists, create one
            logdir = "data/" + service + "/"
            if not path.exists(logdir):
                makedirs(logdir)

            # log IM status to file
            log = open(logdir + logfile + ".csv", "a+")
            statusCheck(log, service)
            log.close()

    else:
        print("Outside opening hours")

    # Calculates seconds left in current minute
    secs = 60 - int(strftime("%S"))
    # Counts down until the next minute
    for var in range(secs, 0, -1):
        stdout.write("\rRunning again in %ss " % var)
        stdout.flush()
        sleep(1)
    stdout.write("\r" + " "*28 + "\n")
    stdout.flush()
