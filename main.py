__author__ = 'articuno'

import requests
import os
LOGIN_URL = "https://anulib.anu.edu.au/using-the-library/book-a-library-group-study-room/index.html"


def ddFormat(num):
    return str(num) if (num >= 10) else return ('0' + str(num)) 


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
    ''' returns string denoting success/failure & reason '''
    with requests.Session() as s:
        p = s.post(LOGIN_URL, data = getAccountDetails(os.environ['ANU_USER'], os.environ['ANU_PASS']))
        q = s.post(p.url, data = getBranchDetails('Chifley', dayMonthToISO(22, 6)))
        if (q.text.count('closed') > 4):
            return "Error: library closed that day"
        r = s.post(q.url, data = getRoomDetails('Chifley', 22, 9, 00, 90, '3.04'))
        if (r.text.count('Sorry') > 0):
            if (r.text.count('conflicts') > 0):
                return "Error: conflicts with another booking"
            else:
                return "Error: Generic error, please report"
        return "Room was (probably) booked successfully"

print(run())
