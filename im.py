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
from numpy import arange                # barcode plot x-axis
from os import makedirs, path           # verifying log directory
from sys import stdout                  # reuse output lines
from time import strftime, sleep        # time formats, timed execution
from urllib.request import urlretrieve  # download status gifs

# plotting on headless server
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


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

    # TODO: this code isn't functional, copied from Manchester-specific version
    elif currentTime == "09:00":
        print("Beginning data analysis")

        # This files is the log from the most recent shift
        with open("logs/" + logfile, newline="") as log:
            log = list(reader(log, delimiter=","))
            logTimes = [entry[0] for entry in log]
            logStati = [1 if entry[1] == "online" else 0 for entry in log]

        # This file contains a cummulative record from all logs
        with open("stats/data.csv", newline="") as data:
            stats = list(reader(data, delimiter=","))
            statTimes = [entry[0] for entry in stats]
            statTally = [int(entry[1]) for entry in stats]
            statTotal = [int(entry[2]) for entry in stats]

        # Add log status' to the cummulative record
        for x in range(0, len(logTimes)):
            ind = statTimes.index(logTimes[x])
            if logStati[x] == 1:
                statTally[ind] += 1
            statTotal[ind] += 1

        # Calculate probabilities
        statCount, statProbs = [x+1 for x in range(0, len(statTotal))], []
        for ind in range(0, len(statTotal)):
            statProbs.append(statTally[ind]/statTotal[ind])

        # Writes updated data back to the cummulative record
        with open("stats/data.csv", "w+") as data:
            for x in range(0, len(statTimes)):
                dataLine = [statTimes[x], str(statTally[x]), str(statTotal[x])]
                data.write(",".join(dataLine)+"\n")

        # Plots uptime for given day
        fig1 = plt.figure()
        y = logStati
        x = arange(len(logStati))
        plt.bar(x, y, width=1.0)
        plt.title(logfile + " between " + logTimes[0] + " & " + logTimes[-1])
        plt.axis('off')
        plt.savefig("stats/" + logfile + ".png")

        # Plots probability scatter graph
        fig2 = plt.figure()
        plt.plot(statCount, statProbs)
        plt.title("Graph of Chance of IM Availability")
        plt.xlabel("Time")
        plt.ylabel("Probability")
        plt.savefig("stats/probs.png")

        print("Data analysis complete!")

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
