from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#For creating Restaurant
"""
myFirstRestaurant = Restaurant(name = "Pizza Palace")
session.add(myFirstRestaurant)
session.commit()
session.query(Restaurant).all()

#For creating Menu Item
cheesePizza = MenuItem(name = "Cheese Pizza", description = "Made with all natural ingredients and fresh Mozarella", course = "Entree", price = "$8.99", restaurant = myFirstRestaurant)
session.add(cheesePizza)
session.commit()
session.query(MenuItem).all()

#For Reading
firstResult = session.query(Restaurant).first()
firstResult.name
"""

items = session.query(MenuItem).all()
for item in items:
	print item.name

veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for veggieBurger in veggieBurgers:
	print veggieBurger.id
	print veggieBurger.price
	print veggieBurger.restaurant.name
	print "\n"

UrbanVeggieBurger = session.query(MenuItem).filter_by(id = 10).one()
print UrbanVeggieBurger.price

UrbanVeggieBurger.price = '$2.99'
session.add(UrbanVeggieBurger)
session.commit()

veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for veggieBurger in veggieBurgers:
	print veggieBurger.id
	print veggieBurger.price
	print veggieBurger.restaurant.name
	print "\n"

spinach = session.query(MenuItem).filter_by(name = "Spinach Ice Cream").one()
print spinach.restaurant.name
session.delete(spinach)
session.commit()