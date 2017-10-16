from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits)
					for x in xrange(32))
	login_session['state'] = state
	# return "The current session state is %s" % login_session['state']
	return render_template('login.html', STATE=state)

#Connect through google account
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output

#Disconnect google account
@app.route('/disconnect')
def disconnect():
	access_token = login_session.get('access_token')
	if access_token is None:
		print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	print 'In gdisconnect access token is %s', access_token
	print 'User name is: '
	print login_session['username']
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
		flash('User %s logged out' % login_session['username'])
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		return redirect(url_for('homepage'))
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response

#Helper functions 
def getUserID(email):
	try:
		user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None

def createUser(login_session):
	newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

#JSON endpoint
@app.route('/catalog.json')
def apiJSON():
	categories = session.query(Category).all()
	categoryJSON = [c.serialize for c in categories]
	for cat in range(len(categories)):
		items = [i.serialize for i in session.query(Item).filter_by(category_id=categoryJSON[cat]["id"]).all()]
		if items:
			categoryJSON[cat]["Item"] = items
	return jsonify(Category=categoryJSON)

# Homepage
@app.route('/')
def homepage():
	categories = session.query(Category).order_by(asc(Category.name))
	items = session.query(Item).order_by(desc(Item.id))
	if 'username' in login_session:
		return render_template('homepage.html', categories=categories, items=items, username=login_session['username'])
	else:
		return render_template('homepage.html', categories=categories, items=items)

#Add new Item
@app.route('/catalog/items/add', methods=['GET', 'POST'])
def addItem():
	if request.method == 'GET':
		categories = session.query(Category).all()
		return render_template('add-item.html', categories=categories)
	else:
		newItem = Item(user_id=login_session['user_id'], name=request.form['title'], description=request.form['description'], category_id=request.form['category'])
		session.add(newItem)
		session.commit()
		flash('New item added!')
		return redirect(url_for('homepage'))

#Edit Item
@app.route('/catalog/<item>/edit', methods=['GET', 'POST'])
def editItem(item):
	categories = session.query(Category).all()
	itemToEdit = session.query(Item).filter_by(name=item).one()
	if request.method == 'GET':
		return render_template('edit-item.html', item=itemToEdit, categories=categories)
	if request.method == 'POST':
		editedItem = Item(user_id=login_session['user_id'], name=request.form['title'], description=request.form['description'], category_id=request.form['category'])
		session.delete(itemToEdit)
		session.commit()
		session.add(editedItem)
		session.commit()
		flash('%s Successfully Edited' % itemToEdit.name)
		session.commit()
		return redirect(url_for('homepage'))

#Delete Item
@app.route('/catalog/<item>/delete', methods=['GET', 'POST'])
def deleteItem(item):
	itemToDelete = session.query(Item).filter_by(name=item).one()
	if request.method == 'GET':
		return render_template('delete-item.html', item=itemToDelete)
	if request.method == 'POST':
		session.delete(itemToDelete)
		flash('%s Successfully Deleted' % itemToDelete.name)
		session.commit()
		return redirect(url_for('homepage'))

#See specific category
@app.route('/catalog/<category>/items')
def oneCategory(category):
	categories = session.query(Category).order_by(asc(Category.name))

	category = session.query(Category).filter_by(name=category).one()
	itemsCategory = session.query(Item).filter_by(category_id=category.id).all()
	return render_template('one-category.html', categories=categories, itemsCategory=itemsCategory, category=category)

#See specific item
@app.route('/catalog/<category>/<item>')
def oneItem(category, item):
	itemDatabase = session.query(Item).filter_by(name=item).one()
	return render_template('one-item.html', item=itemDatabase)


if __name__ == '__main__':
	app.secret_key = 've42q2PO099mkjuAAwsdfdlr'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)