from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///projectrestaurant.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
	restaurants = session.query(Restaurant).all()
	return render_template('restaurants.html', restaurants=restaurants)

#For adding a new restaurant
@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		newRestaurant = Restaurant(name=request.form['nameRestaurant'])
		session.add(newRestaurant)
		session.commit()
		flash("New Restaurant created!!")
		return redirect(url_for('restaurants'))
	else:
		return render_template('newrestaurant.html')
	
#For editing a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	editedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if request.form['nameRestaurant']:
			editedRestaurant.name = request.form['nameRestaurant']
		session.add(editedRestaurant)
		session.commit()
		flash("Restaurant edited!!")
		return redirect(url_for('restaurants'))
	else:
		return render_template(
			'editrestaurant.html', restaurant_id=restaurant_id, editedRestaurant=editedRestaurant)

#For deleting a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	selectedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		if selectedRestaurant:
			session.delete(selectedRestaurant)
			session.commit()
			flash("Restaurant deleted!!")
		return redirect(url_for('restaurants'))
	else:
		return render_template('deleterestaurant.html', restaurant=selectedRestaurant)

#show menu items from a restaurant
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	return render_template('menu.html', restaurant=restaurant, items=items)


#New Menu Item 
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(
			name=request.form['name'], restaurant_id=restaurant_id)
		session.add(newItem)
		session.commit()
		flash("new menu item created!!")
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('newmenuitem.html', restaurant_id=restaurant_id)

#Edit Menu Item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/',
		   methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
	editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		session.add(editedItem)
		session.commit()
		flash("menu item edited!!")
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template(
			'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)

#For deleting a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	selectedItem = session.query(MenuItem).filter_by(id=menu_id).one()
	if request.method == 'POST':
		if selectedItem:
			session.delete(selectedItem)
			session.commit()
			flash("menu item deleted!!")
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('deletemenuitem.html', item=selectedItem)

###Making an API Endpoint (GET Request)
@app.route('/restaurants/JSON/')
def restaurantsJSON():
	restaurants = session.query(Restaurant).all()
	return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON/')
def MenuJSON(restaurant_id, menu_id):
	item = session.query(MenuItem).filter_by(id = menu_id).one()
	return jsonify(MenuItem = item.serialize)

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)