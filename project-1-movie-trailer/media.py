#Python Data Structure (Class) Movie
class Movie():
	def __init__(self, title, description, image_url, trailer_url):
		self.title					= title
		self.movie_storyline		= description
		self.poster_image_url		= image_url
		self.trailer_youtube_url	= trailer_url

	def show_trailer(self):
		webbrowser.open(self.trailer_youtube_url)