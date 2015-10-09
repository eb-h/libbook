__author__ = 'Eric'

import requests
import getopt
import sys
import os
import datetime
from enum import Enum
LOGIN_URL = "https://anulib.anu.edu.au/using-the-library/book-a-library" + \
"-group-study-room/index.html"
USAGE_STRING = "Usage: python3 main.py [--daysFromNowFlag] [-l library] [-h hour] [-m minute] \
        [-d day] [-o month] [-e length] [-r room]"


options, remainder = getopt.getopt(sys.argv[1:], 'l:h:m:d:o:e:r:', ['library=',
                                                                    'day=',
                                                                    'month=',
                                                                    'hour=',
                                                                    'minute=',
                                                                    'length=',
                                                                    'room=',
                                                                    'daysFromNowFlag='])



def parseArgs():
    library = 'Hancock'
    day = 10
    month = 10
    hour = 12
    minute = 30
    length = 120
    room = '3.39'
    daysFromNowFlag = True
    for opt, arg in options:
        if opt in ('-l', '--library'):
            if (arg != 'Chifley' and
                    arg != 'Hancock' and arg != 'Law'):
                quit(USAGE_STRING)
            library = arg
        elif opt == '--daysFromNowFlag':
            daysFromNowFlag = True
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
            if (0 > int(arg) or 60 < int(arg)):
                quit(USAGE_STRING)
            minute = int(arg)
        elif opt in ('-e', '--length'):
            if (1 > int(arg) or 120 < int(arg) or int(arg) % 15 != 0):
                quit(USAGE_STRING)
            length = int(arg)
        elif opt in ('-r', '--room'):
            room = str(arg)
    return library, day, month, hour, minute, length, room, daysFromNowFlag


def ddFormat(num):
    return str(num) if (num >= 10) else ('0' + str(num))


# expects (dd, mm), outputs `2015-mm-dd`
def dayMonthToISO(day, month):
    return '2015-' + ddFormat(month) + '-' + ddFormat(day)


def getAccountDetails(username, password):
    return dict([
        ('inp_uid', username),
        ('inp_passwd', password)])


def getBranchDetails(building, day, month, daysFromNowFlag):
    payload = [
        ('ajax', '1'),
        ('building', building),
        ('bday', dayMonthToISO(day, month)),
        ('showBookingsForSelectedBuilding', '1')]
    if daysFromNowFlag:
        bookingDate = datetime.date.today() + datetime.timedelta(days=day)
        payload[2] = ('bday', dayMonthToISO(bookingDate.strftime('%d'), 
            bookingDate.strftime('%m')))
    return payload


def getRoomDetails(building, day, month, hour, minute, length, room, daysFromNowFlag):
    payload = [
        ('ajax', '1'),
        ('building', building + '+Library'),
        ('bday', dayMonthToISO(day, month)),
        ('bhour', ddFormat(hour)),
        ('bminute', ddFormat(minute)),
        ('bookingPeriod', length),
        ('room_no', room),
        ('submitBooking', '1')]
    if daysFromNowFlag:
        bookingDate = datetime.date.today() + datetime.timedelta(days=day)
        payload[2] = ('bday', dayMonthToISO(bookingDate.strftime('%d'), 
            bookingDate.strftime('%m')))
    return payload


def writeToLogFile(nameOfFile, textToWrite):
    """ Note: Writes over the file if it already exists """
    with open(nameOfFile, 'w') as f:
        f.write(textToWrite)


BookingState = Enum('BookingState', 'Successful LibraryClosed ConflictingBooking GenericBookingException')


def makeBooking(library, day, month, hour, minute, length, room, user, pwd, daysFromNowFlag):
    ''' returns string denoting success/failure & reason '''
    with requests.Session() as s:
        p = s.post(LOGIN_URL, data=getAccountDetails(
            user, pwd))
        q = s.post(p.url, data=getBranchDetails(
            library, day, month, daysFromNowFlag))
        if (q.text.count('closed') > 4):
            raise LibraryClosed
            return "Error: library closed that day"
        r = s.post(q.url, data=getRoomDetails(
            library, day, month, hour, minute, length, room, daysFromNowFlag))
        if (r.text.count('Sorry') > 0):
            if (r.text.count('conflicts with another booking') > 0):
                raise ConflictingBooking
                return "Error: room booked by someone else at that time"
            elif (r.text.count('already have two bookings') > 0):
                return "Error: Maximum of two bookings per day already reached"
            elif (r.text.count('you already booked') > 0):
                raise ConflictingBooking
                return "Error: conflicts with your other bookings"
            else:
                writeToLogFile('log', r.text)
                raise GenericBookingException
                return "Error: Generic error, please report"
        if (r.text.count('You have made the following booking:') > 0):
            return "Room was (probably) booked successfully"
        else:
            writeToLogFile('log', r.text)
            raise GenericBookingException
            return "Error: Generic error, please report"

if __name__ == "__main__":
    library, day, month, hour, minute, length, room, daysFromNowFlag = parseArgs()
    user = os.environ['ANU_USER1']
    pwd = os.environ['ANU_PASS1']
    print(makeBooking(library = library, day = day, month = month, hour = hour, minute = minute, length = length, room = room, user=user, pwd = pwd, daysFromNowFlag = daysFromNowFlag))
