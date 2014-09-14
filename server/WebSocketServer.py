from SimpleWebSocketServer import WebSocket, SimpleWebSocketServer
import requests
import json
import sqlite3
import re
import os
import sys
from Queue import Queue

reload(sys)
sys.setdefaultencoding('UTF-8')

user    = 'wikigraph69'
passw   = 'hitlersucks69'

baseurl = 'https://en.wikipedia.org/w/api.php'
params  = '?action=login&lgname=%s&lgpassword=%s&format=json'% (user,passw)

# login request
r1 = requests.post(baseurl+params)
token = r1.json()['login']['token']

# confirm token; should give "Success"
params2 = params+'&lgtoken=%s'% token
r2 = requests.post(baseurl+params2,cookies=r1.cookies)

class Socket(WebSocket):
    
    def req(self, page):
        params3 = '?action=query&titles=' + page + '&prop=links&pllimit=900&format=json'
        r3 = requests.post(baseurl+params3,cookies=r1.cookies)
        try:
            return r3.json()['query']['pages'].itervalues().next()['links']
        except:
            return None
    
    def compute(self, fr, to):
        # destroy the old db if it exists
        try:
            os.remove(r'/tmp/treedb.db')
        except:
            pass
        
        # create new db
        conn = sqlite3.connect(r'/tmp/treedb.db')
        
        # create the table
        conn.execute('''CREATE TABLE LINKS
            (NAME TEXT NOT NULL,
            PARENT INT);''')
        self.sendMessage("Creating links table")
        
        # insert first page to db
        cursor = conn.cursor()
        result = cursor.execute("INSERT INTO LINKS (NAME, PARENT) VALUES (:pageName, NULL)", {'pageName':fr})
        
        # start queue and insert first page
        queue = Queue(maxsize=0)
        queue.put({'title':str(fr),'id':1})
        
        # while there are still pages to iterate
        while not queue.empty():
            # get the next page to process
            page = queue.get()
        
            #check that the page name is not bogus
            if page['title'] == None:
                self.sendMessage("Skipping page: " + str(page['title']))
                continue
            else:
                self.sendMessage("Reading page: " + str(page['title']))
            
            # check if we found Hitler, exit if it is
            if page['title'] == str(to):
                self.sendMessage(str(to) + " found!")
                break

            # add all the page's links to the queue to be processed
            data = self.req(page['title'])
            if data is None: continue
            for link in data:
                # check that the page hasn't already been processed
                result = conn.execute("SELECT NAME, PARENT FROM LINKS WHERE NAME=:pageName", {'pageName':link['title']})
                if result.fetchone() is None:
                    # add a row to the db
                    cursor = conn.cursor()
                    result = cursor.execute("INSERT INTO LINKS (NAME, PARENT) VALUES (:pageName, :parent)", {'pageName':link['title'], 'parent':page['id']})
                    # add the page to the queue
                    #self.sendMessage("Adding page to queue: " + str(link['title']))
                    queue.put({'title':link['title'],'id':cursor.lastrowid})
                    continue
                else:
                    #self.sendMessage("Already visited page: " + str(link['title']))
                    pass

        # print page trace
        parent = conn.cursor().execute("SELECT NAME, PARENT FROM LINKS WHERE NAME=:pageName", {'pageName':to}).fetchone()

        self.sendMessage("")
        self.sendMessage("Page trace:")

        while parent is not None:
            self.sendMessage(" + " + str(parent[0]))
            parent = conn.cursor().execute("SELECT NAME, PARENT FROM LINKS WHERE ROWID=:id", {'id':parent[1]}).fetchone()
    
    def handleMessage(self):
        if self.data is None:
            self.data = ''
        
        # get the command and arguments
        args = re.split(r'\:\:', str(self.data))
        cmd = args.pop(0);
        
        # commands functionality
        try:
            # compute command
            if cmd == "compute":
                # check arguments
                if len(args) == 2:
                    if not args[0]:
                        raise Exception("'from' page is empty")
                    elif not args[1]:
                        raise Exception("'to' page is empty")
                    else:
                        # run compute
                        self.compute(args[0], args[1])
                else:
                    raise Exception("incorrect number of arguments")
            # getAutocomplete command
            elif cmd == "getAutocomplete":
                # check arguments
                if len(args) == 1:
                    if not args[0]:
                        raise Exception("'from' page is empty")
                    else:
                        #run getAutocomplete
                        self.getAutocomplete(args[0])
                else:
                    raise Exception("incorrect number of arguments")
            # catch excess messages
            else:
                self.sendMessage("invalid command: " + cmd)
        # error output
        except Exception as e:
            self.sendMessage(cmd + ": " + str(e))

    def handleConnected(self):
        print self.address, 'socket: connection established'

    def handleClose(self):
        print self.address, 'socket: connection closed'

server = SimpleWebSocketServer('', 8000, Socket)
server.serveforever()