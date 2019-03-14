import os, webapp2, jinja2
import urllib
from google.appengine.api import users
from google.appengine.ext import ndb

# templates_folder = current_folder + "\\templates"
current_folder = os.path.dirname(__file__)
templates_folder = os.path.join(current_folder, "templates")
environment = jinja2.Environment(loader = jinja2.FileSystemLoader(templates_folder))

DEFAULT_GERNE = 'action'

def movie_key(gerne_name=DEFAULT_GERNE):
    """Constructs a Datastore key for a Gerne entity.
    We use gerne_name as the key.
    """
    return ndb.Key('Gerne', gerne_name)

def title_key(title=''):
    return ndb.Key('title', title)

class Movie(ndb.Model):
    """Sub model for representing an author."""
    title = ndb.StringProperty(indexed=False)
    director = ndb.StringProperty(indexed=False)
    actor1 = ndb.StringProperty(indexed=False)
    actor2 = ndb.StringProperty(indexed=False)
    year = ndb.StringProperty(indexed=False)
    duration = ndb.StringProperty(indexed=False)
    gerne = ndb.StringProperty(indexed=False)
    rent = ndb.StringProperty(indexed=False)
    buy = ndb.StringProperty(indexed=False)
    isrent = ndb.BooleanProperty(indexed=False)
    isbought = ndb.BooleanProperty(indexed=False)


class Index(webapp2.RequestHandler):
    def get(self):
        movies = Movie.query().fetch(50)
        # self.write(movies)
        template_values = {
            'movies': movies,
            'action': 'action',
            'animated': 'animated',
            'comedy': 'comedy',
            'documentary': 'documentary',
            'drama': 'drama',
            'horror': 'horror',
            'musical': 'musical',
            'scifi': 'scifi'
        }
        template = environment.get_template('index.html')
        self.response.write(template.render(template_values))

class Enter(webapp2.RequestHandler):
    def get(self):
        gerne = self.request.get("gerne_name", DEFAULT_GERNE).lower()
        contents = {
            'gerne_name': gerne,
            'all_filled': True
        }
        template = environment.get_template('enter.html')
        self.response.out.write(template.render(contents))

    def post(self):
        gerne = self.request.get("gerne_name", DEFAULT_GERNE).lower()
        movie = Movie(parent=movie_key(gerne))
        movie.title = self.request.get("title").lower()
        movie.director = self.request.get("director").lower()
        movie.actor1 = self.request.get("actor1").lower()
        movie.actor2 = self.request.get("actor2").lower()
        movie.year = self.request.get("year").lower()
        movie.duration = self.request.get("duration").lower()
        movie.gerne = self.request.get("gerne_name", DEFAULT_GERNE).lower()
        movie.rent = self.request.get("rent")
        movie.buy = self.request.get("buy")
        movie.isrent = False
        movie.isbought = False

        all_filled = movie.title!='' and movie.director!='' and movie.year!=''\
                    and movie.duration!='' and movie.rent!='' and movie.buy!=''

        if all_filled:
            movie.put()
            template_values = {
                'all_filled': all_filled
            }
            print all_filled
            self.redirect('/')
        else:
            template_values = {
                'gerne_name': gerne,
                'all_filled': all_filled
            }
            template = environment.get_template('enter.html')
            self.response.write(template.render(template_values))
            print all_filled
            #self.redirect('/?' + urllib.urlencode(query_params))


class Search(webapp2.RequestHandler):
    def get(self):
        gerne = self.request.get("gerne_name", DEFAULT_GERNE).lower()
        contents = {
            'gerne_name': gerne,
            'non_filled': False
        }
        template = environment.get_template('search.html')
        self.response.out.write(template.render(contents))

    def post(self):
        title = self.request.get("title").lower()
        director = self.request.get("director").lower()
        actor1 = self.request.get("actor1").lower()
        year = self.request.get("year").lower()
        gerne_name = self.request.get("gerne_name", DEFAULT_GERNE).lower()

        title_fill = title!=''
        director_fill = director!=''
        actor1_fill = actor1!=''
        year_fill = year!=''

        template = environment.get_template('search.html')

        # iterate through all (50) movies in database and filtersearch
        # get gerne_name after ?
        gerne_name = self.request.get('gerne_name', DEFAULT_GERNE)
        # query only a specific gerne
        movies_query = Movie.query(ancestor=movie_key(gerne_name))
        # get all queries with 'gerne_name' = gerne_name
        movies = movies_query.fetch(50)

        # counting
        non_filled = 4
        no_match = True
        movie_list = []
        for item in movies:
            # print gerne_name
            # print item.title.lower() + ' is ' + item.gerne.lower()
            if (item.gerne.lower() == gerne_name):
                if title_fill:
                    non_filled -= 1
                    if title in item.title.lower():
                        movie_list.append(item)
                        no_match = False
                        print item.title, item.director, item.actor1, item.actor2, item.year, item.duration
                elif director_fill:
                    non_filled -= 1
                    if director in item.director.lower():
                        movie_list.append(item)
                        no_match = False
                        print item.title, item.director, item.actor1, item.actor2, item.year, item.duration
                elif actor1_fill:
                    non_filled -= 1
                    if (actor1 in item.actor1.lower() or actor1 in item.actor2.lower()):
                        movie_list.append(item)
                        no_match = False
                        print item.title, item.director, item.actor1, item.actor2, item.year, item.duration
                elif year_fill:
                    non_filled -= 1
                    if year == item.year:
                        movie_list.append(item)
                        no_match = False
                        print item.title, item.director, item.actor1, item.actor2, item.year, item.duration

        if non_filled == 4:
            self.response.out.write(template.render({
                    'non_filled': True,
                    'movies': movie_list,
                    'no_match': no_match
                })
            )
        else:
            self.response.out.write(template.render({
                    'non_filled': False,
                    'movies': movie_list,
                    'no_match': no_match
                })
            )


class Browse(webapp2.RequestHandler):
    def get(self):
        # get gerne_name after ?
        gerne_name = self.request.get('gerne_name').lower()
        print gerne_name
        # query only a specific gerne
        movies_query = Movie.query(ancestor=movie_key(gerne_name))
        print movies_query
        # get all queries with 'gerne_name' = gerne_name
        movies = movies_query.fetch(50)
        # movies = Movie.query().fetch(50)
        print movies
        template_values = {
            'gerne_name': gerne_name,
            'movies': movies
        }
        for item in movies:
            print item.title
        template = environment.get_template('browse.html')
        self.response.write(template.render(template_values))

    def post(self):
        title = self.request.get('title')
        print title
        movies_query = Movie.query(ancestor=movie_key('action'))
        movies = movies_query.fetch(50)
        movie = Movie()
        for item in movies:
            if item.title == title:
                movie = item
        movie.isrent = False
        movie.isbought = False
        movie.put()
        print movie
        movies_query = Movie.query(ancestor=movie_key('action'))
        movies = movies_query.fetch(50)

        # for item in movies:
        #     item.isrent = False
        #     item.put()
        template_values = {
            'gerne_name': 'action',
            'movies': movies
        }
        template = environment.get_template('cart.html')
        self.response.write(template.render(template_values))
        # self.redirect('/cart?' + urllib.urlencode(query_params))


class Cart(webapp2.RequestHandler):
    def get(self):
        # get gerne_name after ?
        isrent = self.request.get('isrent').lower()
        isbought = self.request.get('isbought').lower()
        # query all movies
        movies_query = Movie.query(ancestor=movie_key('action'))
        print movies_query
        # get all queries with 'gerne_name' = gerne_name
        movies = movies_query.fetch(50)
        for item in movies:
            print item.isrent
        template_values = {
            'gerne_name': 'action',
            'movies': movies
        }
        template = environment.get_template('cart.html')
        self.response.write(template.render(template_values))

    def post(self):
        title = self.request.get('title')
        print title
        movies_query = Movie.query(ancestor=movie_key('action'))
        movies = movies_query.fetch(50)
        movie = Movie()
        for item in movies:
            if item.title == title:
                movie = item
        movie.isrent = False
        movie.isbought = False
        movie.put()
        print movie
        movies_query = Movie.query(ancestor=movie_key('action'))
        movies = movies_query.fetch(50)

        # for item in movies:
        #     item.isrent = False
        #     item.put()
        template_values = {
            'gerne_name': 'action',
            'movies': movies
        }
        template = environment.get_template('cart.html')
        self.response.write(template.render(template_values))
        # self.redirect('/cart?' + urllib.urlencode(query_params))




app = webapp2.WSGIApplication([
    ('/', Index),
    ('/enter', Enter),
    ('/search', Search),
    ('/browse', Browse),
    ('/cart', Cart)
], debug = True)