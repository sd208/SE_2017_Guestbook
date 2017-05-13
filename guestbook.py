#!/usr/bin/env python

# Copyright 2016 Google Inc.
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

# [START imports]
import os
import urllib

from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)

# [START Author]
class Author(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    designation = ndb.StringProperty(indexed=False)
    graduation_year = ndb.StringProperty(indexed=False)
    school = ndb.StringProperty(indexed=False)
    major = ndb.StringProperty(indexed=False)
    website = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END Author]

# [START Comment]
class Comment(ndb.Model):
    author = ndb.StructuredProperty(Author)
    author_email = ndb.StringProperty(indexed=False)
    author_first_name = ndb.StringProperty(indexed=False)
    author_last_name = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END Comment]

# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        author_email = self.request.get('author_email')
        print author_email
        if author_email == None or author_email == '' or len(author_email) == 0:
            anonymous_author = Author()
            anonymous_author.put()
            author = anonymous_author
        else:
            query = Author.query(Author.email == author_email)
            # print query
            # print type(query)

            authors = query.fetch(1)
            if authors == None or len(authors) == 0:
                author = Author()
            else:
                author = authors[0]
            # print type(author)
            # print author

        # get all comments of current guestbook
        comments_query = Comment.query(
            ancestor=guestbook_key(guestbook_name)).order(-Comment.date)
        comments = comments_query.fetch()

        # feed values to webpage
        template_values = {
            'author': author,
            'comments': comments,
            'guestbook_name': urllib.quote_plus(guestbook_name),
        }
        # get jinjia template
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    def post(self):
        # create new author object
        author = Author()
        author.email = self.request.get('user_email')
        author.last_name = self.request.get('user_last_name')
        author.first_name = self.request.get('user_first_name')
        author.designation = self.request.get('user_designation')
        author.school = self.request.get('user_school')
        author.graduation_year = self.request.get('user_graduation_year')
        author.major = self.request.get('user_major')
        author.website = self.request.get('user_website')
        author.put()
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        comments_query = Comment.query(
            ancestor=guestbook_key(guestbook_name)).order(-Comment.date)
        comments = comments_query.fetch()
        template_values = {
            'author': author,
            'comments': comments,
            'guestbook_name': urllib.quote_plus(guestbook_name),
        }
        # get jinjia template
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]

# [START guestbook]
class Guestbook(webapp2.RequestHandler):
    def post(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        comment = Comment(parent=guestbook_key(guestbook_name))
        comment.content = self.request.get('content')
        author_email = comment.author_email = self.request.get('author_email')
        comment.author_first_name = self.request.get('author_first_name')
        comment.author_last_name = self.request.get('author_last_name')
        query = Author.query(Author.email == author_email)
        authors = query.fetch(1)
        if authors == None or len(authors) == 0:
            author = Author()
        else:
            author = authors[0]
        comment.author = author
        comment.put()
        query_params = {'guestbook_name': guestbook_name,
                        'author_email': author_email,
                        }
        self.redirect('/?' + urllib.urlencode(query_params))
# [END guestbook]

# [START GoToLogin]
class Login(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        template_values = {
            'guestbook_name': urllib.quote_plus(guestbook_name),
        }
        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(template_values))
# [END GoToLogin]

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
    ('/login', Login),
], debug=True)
# [END app]