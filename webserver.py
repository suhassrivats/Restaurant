import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "</br>"
                    # Add edit and delete links
                    output += "<a href ='/restaurants/%s/edit' >Edit </a> " % restaurant.id
                    output += "</br>"
                    output += "<a href='/restaurants/%s/delete'>Delete</a>" % restaurant.id
                    output += "</br></br>"
                output += "</body></html>"
                self.wfile.write(output)
                # print output
                return

            if self.path.endswith("restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output = "<html><body>"
                output += "<form method='POST' action='/restaurants/new' enctype='multipart/form-data'>"
                output += "<h2>Add a new restaurant</h2>"
                output += "<input type='text' name='newRestaurant'>"
                output += "<input type='submit' value='submit'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                # print output
                return

            if self.path.endswith("/edit"):
                restaurantIdPath = self.path.split('/')
                restaurantId = restaurantIdPath[2]
                print "restaurant id is = ", restaurantId
                updateRestaurantQuery = session.query(
                    Restaurant).filter_by(id=restaurantId).one()

                if updateRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>"
                    output += updateRestaurantQuery.name
                    output += "</h1>"
                    output += "<form action='/restaurants/%s/edit' method='POST' enctype='multipart/form-data'>" % restaurantId
                    output += "<input type='text' name='updateRestaurantName' placeholder=%s>" % updateRestaurantQuery.name
                    output += "<input type='submit' value='submit'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)

            if self.path.endswith("/delete"):
                restaurantIdPath = self.path.split('/')
                print "Restaurant Id path is =", restaurantIdPath
                restaurantId = restaurantIdPath[2]
                print "restaurant id is = ", restaurantId

                if restaurantId:
                    myRestaurantQuery = session.query(
                        Restaurant).filter_by(id=restaurantId).one()
                    if myRestaurantQuery:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        output = ""
                        output += "<html><body>"
                        output += "<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
                        output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantId
                        output += "<input type = 'submit' value = 'Delete'>"
                        output += "</form>"
                        output += "</body></html>"
                        self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurant')

                    # Create a new restaurant object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    # Redirect to '/restaurants' page
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                print 'Edit post method'
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)

                    # Here we have the updated restaurant name
                    messagecontent = fields.get('updateRestaurantName')
                    print messagecontent

                    # Fetch the id of the restaurant to be updated
                    restaurantIdPath = self.path.split('/')
                    restaurantId = restaurantIdPath[2]
                    print restaurantId

                    # We now need to replace the old name with the updaded one
                    updateRestaurantQuery = session.query(
                        Restaurant).filter_by(id=restaurantId).one()
                    print "updated query is = ", updateRestaurantQuery

                    if updateRestaurantQuery != []:
                        updateRestaurantQuery.name = messagecontent[0]
                        session.add(updateRestaurantQuery)
                        session.commit()

                        # Redirect to '/restaurants' page
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                restaurantIdPath = self.path.split('/')
                restaurantId = restaurantIdPath[2]
                print "restaurant id is = ", restaurantId

                myRestaurantQuery = session.query(
                    Restaurant).filter_by(id=restaurantId).one()
                print 'The restaurant to be deleted is: ', myRestaurantQuery

                if myRestaurantQuery:
                    session.delete(myRestaurantQuery)
                    session.commit()

                    # Redirect to '/restaurants' page
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()


if __name__ == '__main__':
    main()
