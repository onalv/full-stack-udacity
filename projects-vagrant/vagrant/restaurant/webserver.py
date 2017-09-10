from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#database configuration
engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
#####

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			"""
			if self.path.endswith("/hello"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "Hello!"
				output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			"""

			#Show all restaurants
			if self.path.endswith("/restaurants"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()


				output = ""
				output += "<html><body>"
				output += "<h2>All the restaurants!!</h2><br>"
				
				#getting restaurants from database
				restaurants = session.query(Restaurant).all()
				for restaurant in restaurants:
					output += "<p>%s</p>" % restaurant.name
					output += "<a href='/restaurant/%s/edit'>Edit</a>  |  " % restaurant.id
					output += "<a href='/restaurant/%s/delete'>Delete</a>" % restaurant.id

				output += "<a href='/restaurants/new'><h3>Create a new restaurant here:</h3></a>"
				output += "</body></html>"


				self.wfile.write(output)
				print output
				return

			#Create new restaurant
			elif self.path.endswith("/restaurants/new"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "<h2>Create a new restaurant</h2>"
				output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
				output += "<h2>Write the name of the new restaurant to create</h2>"
				output += "<input name='restaurant' type='text' ><input type='submit' value='Submit'></form>"
				output += "<a href='/restaurants'><h3>Back to restaurants</h3></a>"
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

			elif self.path.endswith("/edit"):
				restaurantID = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantID).one()

				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					output = ""
					output += "<html><body>"
					output += "<h2>Edit %s</h2>" % myRestaurantQuery.name
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/edit'>" % restaurantID				
					output += "<input name='newRestaurantName' type='text' placeholder='%s'><input type='submit' value='Rename'></form>" % myRestaurantQuery.name
					output += "<a href='/restaurants'><h3>Back to restaurants</h3></a>"
					output += "</body></html>"

					self.wfile.write(output)
					print output
					return

			elif self.path.endswith("/delete"):
				restaurantID = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantID).one()

				if myRestaurantQuery != []:
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					output = ""
					output += "<html><body>"
					output += "<h2>Are you sure you want to delete %s restaurant?</h2>" % myRestaurantQuery.name
					output += "<form method='POST' enctype='multipart/form-data' action='/restaurant/%s/delete'>" % restaurantID				
					output += "<input type='submit' value='Delete'></form>"
					output += "<a href='/restaurants'><h3>Back to restaurants</h3></a>"
					output += "</body></html>"

					self.wfile.write(output)
					print output
					return

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			self.send_response(301)
			self.end_headers()

			

			"""
			if self.path.endswith("/hello"): 
				output = ""
				output += "<html><body>"
				output += " <h2> Okay, how about this: </h2>"
				output += "<h1> %s </h1>" % messagecontent[0] 

				output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
				output += "</body></html>"
				self.wfile.write(output)
				print output
				return
			"""

			if self.path.endswith("restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
					messagecontent = fields.get('restaurant')

				restaurantName = messagecontent[0]

				#add restaurant to the database
				newRestaurant = Restaurant(name = restaurantName)
				session.add(newRestaurant)
				session.commit()

				output = ""
				output += "<html><body>"
				output += "<h2>New restaurant %s created!!</h2>" % newRestaurantName
				output += "<a href='/restaurants'><h3>Back to restaurants</h3></a>"
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
				
				messagecontent = fields.get('newRestaurantName')
				restaurantID = self.path.split("/")[2]
				
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantID).one()

				#modify restaurant in the database
				if myRestaurantQuery != [] :
					myRestaurantQuery.name = messagecontent[0]
					session.add(myRestaurantQuery)
					session.commit()

				output = ""
				output += "<html><body>"
				output += "<h2>Restaurant name changed!!</h2>"
				output += "<a href='/restaurants'><h3>Back to restaurants</h3></a>"
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
								
				restaurantID = self.path.split("/")[2]
				
				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantID).one()

				#modify restaurant in the database
				if myRestaurantQuery != [] :					
					session.delete(myRestaurantQuery)
					session.commit()

				output = ""
				output += "<html><body>"
				output += "<h2>Restaurant deleted!!</h2>"
				output += "<a href='/restaurants'><h3>Back to restaurants</h3></a>"
				output += "</body></html>"

				self.wfile.write(output)
				print output
				return

		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('', port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__=='__main__':
	main()