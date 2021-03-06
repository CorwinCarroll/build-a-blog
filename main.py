#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t_pages = jinja_env.get_template(template)
		return t_pages.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
	title = db.StringProperty(required = True)
	blogpost = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)

class Main(Handler):
	def get(self):
		self.redirect("/blog")

class NewPost(Handler):
	def render_front(self, title="", blogpost="", error=""):
		blogposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC ")

		self.render("form.html", title=title, blogpost=blogpost, error=error, blogposts=blogposts)

	def get(self):
		self.render_front()

	def post(self):
		title = self.request.get("title")
		blogpost = self.request.get("blogpost")

		if title and blogpost:
			bp = BlogPost(title = title, blogpost = blogpost)
			bp.put()

			self.redirect("/blog")
		else:
			error = "We need both a title and a post to publish. Give it another go!"
			self.render_front(title, blogpost, error)

class Confirmation(Handler):
	def render_confirmation(self):
		self.render("confirm.html")

	def get(self):
		self.render_confirmation()

	def post(self):
		title = self.request.get("title")
		blogpost = self.request.get("blogpost")



class Blog(Handler):
	def render_blog(self, title="", blogpost="", error=""):
		all_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5 ")

		self.render("blog.html", title=title, blogpost=blogpost, error=error, all_posts=all_posts)

	def get(self):
		self.render_blog()

class ViewPost(Handler):

	def view_post(self, id):

		blogpost = BlogPost.get_by_id( int(id) )

		if blogpost: 
			self.render("post.html", blogpost=blogpost)
		else:
			self.render("notfound.html")


	def get(self, id):
		self.view_post(id)


app = webapp2.WSGIApplication([
	('/', Main),
	('/newpost', NewPost),
	('/blog', Blog),
	('/confirmation', Confirmation),
	webapp2.Route('/blog/<id:\d+>', ViewPost)
], debug=True)