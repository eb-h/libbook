import os
from booking import makeBooking

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
'''
makeBooking(library="Hancock",
                day=5,
                month=1,
                hour=18,
                minute=00,
                length=60,
                room=3.39,
                user=users[0],
                pwd=passes[0],
                daysFromNowFlag=True)
'''

assert(len(users) == len(passes))
for time in range(5):
    for accNum in range(len(users)):
        try: 
            makeBooking(library="Hancock",
                day=7,
                month=1,
                hour=9 + time*2,
                minute=00,
                length=105,
                room=3.39,
                user=users[accNum],
                pwd=passes[accnum],
                daysFromNowFlag=True)
            break
        except Exception
            print("")
        """
        except LibraryClosed:
            print("Error, Library Closed")
        except ConflictingBooking:
            print("Error, Conflicting Booking")
        except GenericBookingException:
            print("Error, something went wrong")
            """
