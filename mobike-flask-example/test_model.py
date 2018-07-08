from model import User, getUser, addUser, removeUser
from model import Lock, getLock, addLock, removeLock
from model import RentalPeriod, getRentals, addRental, removeRental

from datetime import datetime, timedelta #create timestamps of now
from pytz import timezone
import unittest
import settings, random, string

class test_user(unittest.TestCase):
	userID    = None
	startUser = None

	def setUp(self):
		#add user to database & keep id
		self.startUser = User(userName='test')
		self.userID    = addUser(self.startUser)

	def test_retrieve(self):
		user = getUser(self.userID) #retrieve user
		self.assertEqual(user,self.startUser) #

	def test_json(self):
		userDict = self.startUser.toJson()
		self.assertEqual(userDict['userName'], self.startUser.userName)

	def test_remove(self):
		removeUser(self.startUser) #remove user
		user = getUser(self.userID) #try to retrieve the user
		self.assertEqual(None, user) #shouldn't work

	def tearDown(self):
		removeUser(self.startUser) #remove the user in case something goes wrong
		
class test_lock(unittest.TestCase):
	lockID    = None
	startLock = None

	def setUp(self):
		self.startLock = Lock()
		self.lockID    = addLock(self.startLock)

	def test_retrieve(self):
		lock = getLock(self.lockID)
		self.assertEqual(self.startLock, lock)

	def test_json(self):
		lockDict = self.startLock.toJson()
		self.assertEqual(lockDict['lockID'], self.startLock.lockID)

	def test_remove(self):
		removeLock(self.startLock)
		lock = getLock(self.lockID)
		self.assertEqual(None, lock)

	def tearDown(self):
		removeLock(self.startLock)

class test_rentals(unittest.TestCase):
	userIDA = None
	userA   = None #two users
	userB   = None
	lockA1  = None #user A has 2 locks
	lockA2  = None 
	rentalA1A1 = None # 2 rental periods for LockA1
	rentalA1A2 = None
	rentalA2A1 = None # 1 rental period for lock A2
	rentalDict = None #mock what should be returned
	def setUp(self):
		self.userA = User(userName="test")
		self.userA.userID = addUser(self.userA)
		self.userIDA = self.userA.userID
		self.userB = User(userName="test2")
		self.userB.userID = addUser(self.userB)

		self.lockA1  = Lock()
		self.lockA1.lockID = addLock(self.lockA1)
		self.lockA2  = Lock()
		self.lockA2.lockID = addLock(self.lockA2)

		self.rentalA1A1 = RentalPeriod(\
			userID      = self.userA.userID ,\
			lockID      = self.lockA1.lockID , \
			lockName    = "test lock A1A1" ,\
			startTime   = datetime.now(settings.TIMEZONE), \
			stopTime    = datetime.now(settings.TIMEZONE) + timedelta(hours=1), \
			lockKey     = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))\
		)
		self.rentalA1A1.rentalID = addRental(self.rentalA1A1)
		self.rentalA1A2 = RentalPeriod(\
			userID      = self.userA.userID ,\
			lockID      = self.lockA1.lockID , \
			lockName    = "test lock A1A2" ,\
			startTime   = datetime.now(settings.TIMEZONE) + timedelta(hours=1), \
			stopTime    = datetime.now(settings.TIMEZONE) + timedelta(hours=2), \
			lockKey     = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))\
		)
		self.rentalA1A2.rentalID = addRental(self.rentalA1A2)
		self.rentalA2A1 = RentalPeriod(\
			userID      = self.userA.userID ,\
			lockID      = self.lockA2.lockID , \
			lockName    = "test lock A2A1" ,\
			startTime   = datetime.now(settings.TIMEZONE), \
			stopTime    = datetime.now(settings.TIMEZONE) + timedelta(hours=1), \
			lockKey     = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))\
		)
		self.rentalA2A1.rentalID = addRental(self.rentalA2A1)

		#mock rental output
		self.rentalDict = {}
		
		self.rentalDict[self.lockA1.lockID] = {'lockName' : self.rentalA1A1.lockName , 'rentalPeriods' : []}
		self.rentalDict[self.lockA1.lockID]['rentalPeriods'].append({\
			'startTime' : settings.TIMEZONE.localize(self.rentalA1A1.startTime).isoformat(),\
			'stopTime'  : settings.TIMEZONE.localize(self.rentalA1A1.stopTime ).isoformat(),\
			'lockKey'   : self.rentalA1A1.lockKey\
			})
		self.rentalDict[self.lockA1.lockID]['rentalPeriods'].append({\
			'startTime' : settings.TIMEZONE.localize(self.rentalA1A2.startTime).isoformat(),\
			'stopTime'  : settings.TIMEZONE.localize(self.rentalA1A2.stopTime ).isoformat(),\
			'lockKey'   : self.rentalA1A2.lockKey\
			})

		
		self.rentalDict[self.lockA2.lockID] = {'lockName' : self.rentalA2A1.lockName , 'rentalPeriods' : []}
		self.rentalDict[self.lockA2.lockID]['rentalPeriods'].append({\
			'startTime' : settings.TIMEZONE.localize(self.rentalA2A1.startTime).isoformat(),\
			'stopTime'  : settings.TIMEZONE.localize(self.rentalA2A1.stopTime ).isoformat(),\
			'lockKey'   : self.rentalA2A1.lockKey\
			})

	#userB has no locks
	def test_retrieval_NoLocks(self):
		rentals = getRentals(self.userB.userID)
		self.assertEqual(rentals, {})#note the empty dict instead of None b/c the user simply has no rentals periods

	def test_retrieval_multipleLocks(self):
		rentals = getRentals(self.userA.userID)
		self.assertEqual(rentals, self.rentalDict)

	def test_remove(self):
		removeRental(self.rentalA1A1)
		removeRental(self.rentalA1A2)
		removeRental(self.rentalA2A1)

		removeLock(self.lockA1)
		removeLock(self.lockA2)

		removeUser(self.userA)
		removeUser(self.userB)

		rentals = getRentals(self.userIDA)
		self.assertEqual(rentals , None) #here it is indeed None b/c the user doesn't exist

	def tearDown(self):
		removeRental(self.rentalA1A1)
		removeRental(self.rentalA1A2)
		removeRental(self.rentalA2A1)

		removeLock(self.lockA1)
		removeLock(self.lockA2)

		removeUser(self.userA)
		removeUser(self.userB)

if __name__ == '__main__':
	unittest.main()