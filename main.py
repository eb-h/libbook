__author__ = 'Eric'

import requests
import getopt
import sys
import os
LOGIN_URL = "https://anulib.anu.edu.au/using-the-library/book-a-library"
"-group-study-room/index.html"


options, remainder = getopt.getopt(sys.argv[1:], 'l:h:m:d:r:', ['library=',
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
            if (library != 'Chifley' and
                    library != 'Hancock' and library != 'Law'):
                return "Error: library unknown"
            else:
                library = arg
        elif opt == '--day':
            day = int(arg)
        elif opt == '--month':
            month = int(arg)
        elif opt in ('-h', '--hour'):
            hour = int(arg)
        elif opt in ('-m', '--minute'):
            minute = int(arg)
        elif opt == '--length':
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
            if (r.text.count('conflicts') > 0):
                return "Error: room booked by someone else at that time"
            elif (r.text.count('Already') > 0):
                return "Error: conflicts with your other bookings"
            else:
                return "Error: Generic error, please report"
        return "Room was (probably) booked successfully"

print(run())
