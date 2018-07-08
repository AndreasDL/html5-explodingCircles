from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from datetime import datetime, timedelta #create timestamps of now
from pytz import timezone
import random, string #mock string, might dissappear in future
import settings

#needed as one shared variable between classes so that relations between objects are nicely defined
Base = declarative_base()
#load the engine from the settings.py file, see readme
Engine = create_engine(URL(**settings.DATABASE))
#create session
Session = sessionmaker(Engine)
session = Session()


#USER
#gets a user based on his userID
def getUser(userID):
	user = session.query(User).filter_by(userID = userID).first()
	return user
#add a user (object) to the database
def addUser(user):
	session.add(user)
	session.commit()
	return user.userID
#deletes a user (object) from the database
def removeUser(user):
	session.delete(user)
	session.commit()

#gets the userID with a corresponding token
#TODO: actual resolution from token to userID
def getUserID(token):
	return token

#LOCK
#gets a lock based on his lockID
def getLock(lockID):
	lock = session.query(Lock).filter_by(lockID = lockID).first()
	return lock
#add a lock to the database
def addLock(lock):
	session.add(lock)
	session.commit()
	return lock.lockID
#remove a lock from the database
def removeLock(lock):
	session.delete(lock)
	session.commit()

#LOCK
#gets the rental periods associated with a user
#returns None if user is not found
#returns an empty map is the user has no rentals
def getRentals(userID):
	#check if user exists
	user = getUser(userID)
	if user == None:
		return None

	locks = session.query(RentalPeriod).filter_by(userID = userID).all()

	jsonLocks = {}#dictionary lockID => rental periods
	for lock in locks:
		if lock.lockID not in jsonLocks:
			jsonLocks[lock.lockID] = {'lockName' : lock.lockName, 'rentalPeriods' : [] }

		jsonLocks[lock.lockID]['rentalPeriods'].append({\
			'startTime' : settings.TIMEZONE.localize(lock.startTime).isoformat(),\
			'stopTime' : settings.TIMEZONE.localize(lock.stopTime).isoformat(),\
			'lockKey' : lock.lockKey\
		})
	return jsonLocks

#adds a rentalPeriod (object) to the database
def addRental(rentalPeriod):
	session.add(rentalPeriod)
	session.commit()
	return rentalPeriod.rentalID

#removes a rentalperiod (object) from the database
def removeRental(rentalPeriod):
	session.delete(rentalPeriod)
	session.commit()

#CLASSES
class User(Base):
    __tablename__ = 'Users'

    userID   = Column(Integer, primary_key=True)
    userName = Column(String(150))

    #converts object to a dictionary (map)
    #needed because sqlalchemy's ORM objects have non json friendly stuff
    def toJson(self):
    	return { 'userID' : self.userID , 'userName' : self.userName }


class Lock(Base):
	__tablename__ = 'Locks'
	lockID = Column(Integer, primary_key=True)

    #converts object to a dictionary (map)
    #needed because sqlalchemy's ORM objects have non json friendly stuff
	def toJson(self):
		return { 'lockID' : self.lockID }


class RentalPeriod(Base):
	__tablename__ = 'RentalPeriods'
	rentalID  = Column(Integer, primary_key=True, autoincrement=True)

	lockID    = Column(Integer, ForeignKey('Locks.lockID'))
	userID    = Column(Integer, ForeignKey('Users.userID'))
	startTime = Column(DateTime(timezone=True)) #TODO timestamps
	stopTime  = Column(DateTime(timezone=True))	
	lockKey   = Column(String(50)) #TODO gen hashes
	lockName  = Column(String(50)) #TODO is this clean?


    #converts object to a dictionary (map)
    #needed because sqlalchemy's ORM objects have non json friendly stuff
	def toJson(self):
		print(self.startTime.isoformat())
		return {'lockID' : self.lockID, 'userID' : self.userID, 'startTime' : self.startTime.isoformat(), 'stopTime' : self.stopTime.isoformat() , 'lockName' : self.lockName, 'lockKey' : self.lockKey}

#create tables if they don't exist
Base.metadata.create_all(Engine)

#DEBUG
#adds 1 user with 3 locks for test purposes
'''
def addTestData():
	ed_user = User(userName='ed Jones')
	session.add(ed_user)
	session.commit() #commit needed to get the userID in the local object

	for i in range(0,3):
		ed_lock = Lock()
		session.add(ed_lock)
		session.commit() #commit needed to get the lock id

		startT = datetime.now(settings.TIMEZONE)
		for i in range (0,5):
			stopT = startT + timedelta(hours=1)
			lockKey = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(50))

			ed_rentalPeriod = RentalPeriod(\
				userID=ed_user.userID ,\
				lockID=ed_lock.lockID , \
				lockName="user" + str(ed_user.userID) + "'s lock" ,\
				startTime=startT, \
				stopTime =stopT, \
				lockKey=lockKey\
			)
			session.add(ed_rentalPeriod)
			session.commit()
			startT = stopT

	return "Test data added successful user with id = "\
	 + str(ed_user.userID) + " and a lock with id = " + str(ed_lock.lockID)\
	 + " was added! yay!"
'''