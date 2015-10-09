import os
from booking import makeBooking, BookingState

def getAccounts():
    counter = 1
    users = []
    passes = []
    while (True):
        userString = "ANU_USER" + str(counter)
        passString = "ANU_PASS" + str(counter)
        if userString in os.environ and passString in os.environ:
            users.append(os.environ[userString])
            passes.append(os.environ[passString])
            counter += 1
        else:
            break
    return users, passes

users, passes = getAccounts()


# details
firstHour = 8
roomToBook = 3.37
bookingLength = 105
numberOfBookingsInADay = 5
daysFromNow=6


assert(len(users) == len(passes))
for time in range(numberOfBookingsInADay):
    for accNum in range(len(users)):
        res = makeBooking(library="Hancock",
            day=daysFromNow,
            month=1,
            hour=firstHour + time*2,
            minute=00,
            length=bookingLength,
            room=roomToBook,
            user=users[accNum],
            pwd=passes[accNum],
            daysFromNowFlag=True)
        if res is BookingState.Successful:
            # In future this line should probably include `minute`
            print("Room {0} booked for {1}:00, {2} minutes, by {3}".format(roomToBook, 
                firstHour + time*2, 
                bookingLength, 
                users[accNum]))
            break
        elif res is BookingState.LibraryClosed:
            print('Library is closed at that time')
        elif res is BookingState.MaximumBookingsReached:
            print('{0} unable to book {1} for {2}:00, maximum number of bookings reached'.    
                    format(users[accNum],
                roomToBook, 
                firstHour + time*2))
        elif res is BookingState.ConflictingBooking:
            print('The room has already been booked')
            break
        elif res is BookingState.GenericBookingException:
            print('Generic booking exception. Please check the logs')
