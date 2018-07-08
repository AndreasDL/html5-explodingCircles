#flask
from flask import Flask, abort, request
from flask.ext.sqlalchemy import SQLAlchemy
#model
from model import User, getUser, getUserID, getRentals
import simplejson as json

app = Flask(__name__)

#info about me (own user)
@app.route('/me')
def routeMe():
	#no token given => abort
	if 'Bearer_token' not in request.headers:
		abort(403)

	#get token from headers 
	token = request.headers['Bearer_token']
	userID = getUserID(token) #get userID from token #TODO
	#if token has no corresponding userID (= not valid)
	if userID == None:
		abort(403)
	
	#get user
	user = getUser(userID)
	#(can be removed after the token ~> userID is completed), but is needed now since getUser(token) return the token as mock
	if user == None: 
		abort(403)

	#return json
	return json.dumps({'user' : user.toJson()}, sort_keys=True, indent= 2 * ' '), 200


#get the locks/ rental periods associated with a single user
@app.route('/locks')
def routeLocks():
	#no token given => abort
	if 'Bearer_token' not in request.headers:
		abort(403)

	#get token from headers 
	token = request.headers['Bearer_token']
	userID = getUserID(token) #token ~> userID #TODO
	#if token has no corresponding userID (=not valid)
	if userID == None:
		abort(403)

	#get the locks
	locks = getRentals(userID)

	#return json
	return json.dumps({'locks': locks}, sort_keys=True, indent=2 * ' '), 200


#override default 403 page (bad authentication)
@app.errorhandler(403)
def notAuthenticated(error):
	return json.dumps({'error' : 'authentication not correct, be sure to put the token in the Bearer_token header'}) , 403

#override default 404 page (not found)
@app.errorhandler(404)
def notFound(error):
	return json.dumps({'error' : 'Not Found'}),404

#override default 405 page (method not allowed)
@app.errorhandler(405)
def notAllowed(error):
	return json.dumps({'error' : 'Method not allowed'}), 405

'''
#debug only
@app.route('/addTestData', methods=['post'])
def routeAddTestData():
	return addTestData()
'''
#run app
if __name__ == '__main__':
	app.run(debug=True)