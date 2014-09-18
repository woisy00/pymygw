from tornado.web import RequestHandler
import json
import Database


DB = Database.Database()


class Nodes(RequestHandler):
    def get(self):
        r = DB.get()
        response = json.dumps({'nodes': r})
        self.write(response)


class Node(RequestHandler):
    def get(self, n):
        r = DB.get(Node=n)
        response = json.dumps({n: r})
        self.write(response)

