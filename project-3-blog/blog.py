import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db
from google.appengine.api import users

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'asF232%#.-SASDafubf22a3"$#'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      #self.write('Hello, Blog!')
      self.redirect("/blog")


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


##### blog stuff

class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    #created by me
    created_by = db.StringProperty(required = True)
    number_likes = db.IntegerProperty(required = True) 
    liked_by = db.StringListProperty(required = True) 
    comments = db.ListProperty(db.Text, required = True)
    comment_by_list = db.StringListProperty(required = True)  

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)
"""
class Comment(db.Model):
    content = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DataTimeProperty(auto_now = True)
    created_by = db.StringProperty(required = True)
    post_parent = db.IntegerProperty(required = True)

    #def render(self):
        #self._render_text = self.content.replace('\n', '<br>')
        #return render_str("comment.html", p = self)
"""
class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')
        #first_comment = self.request.get('comment')

        created_by = self.user.name
        number_likes = 0
        liked_by = []
        comments = []
        comment_by_list = []
        #comments.append(first_comment)

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content, created_by = created_by, number_likes = number_likes, liked_by = liked_by, comments = comments, comment_by_list = comment_by_list)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "Subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class EditPost(BlogHandler):
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            if self.user.name != post.created_by:
                error = 'That is not possible. You did not create this Post. Only author can edit it!'
                self.render("error.html", error = error)

            if not post:
                self.error(404)
                return

            self.render("edit.html", p = post)
        else:
            self.redirect("/login")
    
    def post(self, post_id):
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if self.user.name==post.created_by:
            subject = self.request.get('subject')
            content = self.request.get('content')
            #comment = db.Text(self.request.get('comment'))

            if subject and content:
                post.subject = subject
                post.content = content
                #post.comments.append(comment)
                post.put()
                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                error = "subject and content, please!"
                #revisar linea de abajo
                self.render("edit.html", subject=subject, content=content, error=error)
        else: 
            error = 'That is not possible. You did not create this Post. Only author can edit it!'
            self.render("error.html", error = error)

class DeletePost(BlogHandler):
    def get(self, post_id):
        if self.user: 
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            if self.user and self.user.name==post.created_by:
                post.delete()
                self.redirect('/blog')
            else: 
                error = 'That is not possible. You did not create this Post. Only author can delete it!'
                self.render("error.html", error = error)
        else: 
            self.redirect("/login")

class AddComment(BlogHandler): 
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            if not post:
                self.error(404)
                return

            self.render("add-comment.html", p = post)
        else: 
            self.redirect("/login")

    def post(self, post_id):
        if not self.user:
            self.redirect('/blog')

        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        #I create data at the same index for both lists, this way I can relate who created which comment
        comment = db.Text(self.request.get('comment'))
        comment_by = self.user.name

        if comment:
            post.comments.append(comment)
            post.comment_by_list.append(comment_by)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))   

class EditComment(BlogHandler):
    def get(self, post_id, comment_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            if not post:
                self.error(404)
                return

            if post.comment_by_list[int(comment_id)] == self.user.name:
                self.render("edit-comment.html", p = post, comment_index = int(comment_id))                
            else:
                error = 'That is not possible. You can not edit others comment!'
                self.render("error.html", error = error)            
        else: 
            self.redirect("/login")   
    def post(self, post_id, comment_id):
        if not self.user:
            self.redirect('/blog')
        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

        if post.comment_by_list[int(comment_id)] == self.user.name:
            comment = db.Text(self.request.get('comment'))

            if comment:
                post.comments[int(comment_id)] = comment
                post.put()
                self.redirect('/blog/%s' % str(post.key().id()))

class DeleteComment(BlogHandler):
    def get(self, post_id, comment_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            #Will erase if comment was created by the user only.
            if post.comment_by_list[int(comment_id)] == self.user.name:
                post.comments.pop(int(comment_id))
                post.comment_by_list.pop(int(comment_id))
                post.put()
                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                error = 'That is not possible. You can not delete others comment!'
                self.render("error.html", error = error)
        else:
            self.redirect("/login")

class LikePost(BlogHandler):
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            #if is not own post and post haven't been already given a like by actual user then like post
            if self.user.name != post.created_by and self.user.name not in post.liked_by:
                post.number_likes = post.number_likes + 1
                post.liked_by.append(self.user.name)
                post.put()

                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                error = 'That is not possible. You can not like your own post neither can you like a post more than once!'
                self.render("error.html", error = error)
        else:
            self.redirect("/login")

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/welcome')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            #self.redirect('/blog')
            self.redirect('/welcome')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

class Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/login')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),                        
                               ('/blog/deletepost/([0-9]+)', DeletePost),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/likepost/([0-9]+)', LikePost),
                               ('/blog/addcomment/([0-9]+)', AddComment),
                               ('/blog/editcomment/([0-9]+)/([0-9]+)', EditComment),
                               ('/blog/deletecomment/([0-9]+)/([0-9]+)', DeleteComment),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout)
                               ],
                              debug=True)
