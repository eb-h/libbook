__author__ = 'Eric'

import requests
import getopt
import sys
import os
LOGIN_URL = "https://anulib.anu.edu.au/using-the-library/book-a-library" + \
"-group-study-room/index.html"
USAGE_STRING = "Usage: python3 main.py [-l library] [-h hour] [-m minute] \
        [-d day] [-o month] [-e length] [-r room]"


options, remainder = getopt.getopt(sys.argv[1:], 'l:h:m:d:o:e:r:', ['library=',
                                                                    'day=',
                                                                    'month=',
                                                                    'hour=',
                                                                    'minute=',
                                                                    'length=',
                                                                    'room='])


def parseArgs():
    library = 'Chifley'
    day = 1
    month = 1
    hour = 9
    minute = 00
    length = 90
    room = '3.04'
    for opt, arg in options:
        if opt in ('-l', '--library'):
            if (arg != 'Chifley' and
                    arg != 'Hancock' and arg != 'Law'):
                quit(USAGE_STRING)
            library = arg
        elif opt in ('-d', '--day'):
            if (1 > int(arg) or 31 < int(arg)):
                quit(USAGE_STRING)
            day = int(arg)
        elif opt in ('-o', '--month'):
            if (1 > int(arg) or 12 < int(arg)):
                quit(USAGE_STRING)
            month = int(arg)
        elif opt in ('-h', '--hour'):
            hour = int(arg)
        elif opt in ('-m', '--minute'):
            if (1 > int(arg) or 60 < int(arg)):
                quit(USAGE_STRING)
            minute = int(arg)
        elif opt in ('-e', '--length'):
            if (1 > int(arg) or 120 < int(arg) or int(arg) % 15 != 0):
                quit(USAGE_STRING)
            length = int(arg)
        elif opt in ('-r', '--room'):
            room = str(arg)
    return library, day, month, hour, minute, length, room


def ddFormat(num):
    return str(num) if (num >= 10) else ('0' + str(num))


# expects (dd, mm), outputs `2015-mm-dd`
def dayMonthToISO(day, month):
    return '2015-' + ddFormat(month) + '-' + ddFormat(day)


def getAccountDetails(username, password):
    return dict([
        ('inp_uid', username),
        ('inp_passwd', password)])


def getBranchDetails(building, day):
    return dict([
        ('ajax', '1'),
        ('building', building),
        ('bday', day),
        ('showBookingsForSelectedBuilding', '1')])


def getRoomDetails(building, day, month, hour, minute, length, room):
    return dict([
        ('ajax', '1'),
        ('building', building + '+Library'),
        ('bday', dayMonthToISO(day, month)),
        ('bhour', ddFormat(hour)),
        ('bminute', ddFormat(minute)),
        ('bookingPeriod', length),
        ('room_no', room),
        ('submitBooking', '1')])


def run():
    library, day, month, hour, minute, length, room = parseArgs()
    ''' returns string denoting success/failure & reason '''
    with requests.Session() as s:
        p = s.post(LOGIN_URL, data=getAccountDetails(
            os.environ['ANU_USER'], os.environ['ANU_PASS']))
        q = s.post(p.url, data=getBranchDetails(
            library, dayMonthToISO(day, month)))
        if (q.text.count('closed') > 4):
            return "Error: library closed that day"
        r = s.post(q.url, data=getRoomDetails(
            library, day, month, hour, minute, length, room))
        if (r.text.count('Sorry') > 0):
            if (r.text.count('conflicts with another booking') > 0):
                return "Error: room booked by someone else at that time"
            elif (r.text.count('already have two bookings') > 0):
                return "Error: Maximum of two bookings per day already reached"
            elif (r.text.count('you already booked') > 0):
                return "Error: conflicts with your other bookings"
            else:
                with open('logfile', 'w') as f:
                    f.write(r.text)
                return "Error: Generic error, please report"
        return "Room was (probably) booked successfully"

print(run())
