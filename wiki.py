#!/usr/bin/python
import requests
import json
import sqlite3
import re
import os
import sys
from Queue import Queue

def autocomplete(input):
    url="https://en.wikipedia.org/w/api.php?action=query&list=allpages&apfrom=" + input + "&aplimit=5&format=json"
    r5 = requests.post(url)
    r5 = r5.json()['query']['allpages']
    return r5

def req(page):
    params = '?action=query&titles=' + page + '&prop=links&pllimit=900&format=json'
    params3 = params+'&lgtoken=%s'% token
    r3 = requests.post(baseurl+params3,cookies=r1.cookies)
    try:
        return r3.json()['query']['pages'].itervalues().next()['links']
    except:
        return None

def bfs(pageName, parentID):
    cursor = conn.cursor()
    result = cursor.execute("INSERT INTO LINKS (NAME, PARENT) VALUES (:pageName, NULL)", {'pageName':pageName}) 
    queue = Queue(maxsize=0)
    queue.put({'title':pageName,'id':1})
    while not queue.empty():
        # get the next page to process
        page = queue.get()

        #check that the page name is not bogus
        if page['title'] == None or re.search('^\.', page['title']) != None: 
            print "Skipping page: " + page['title']
            continue
        else:
            print "Reading page: " + page['title']

        # check if we found Hitler, exit if it is
        if page['title'] == "Adolf Hitler":
            print("Hitler found!")
            return

        # add all the page's links to the queue to be processed
        try:
            data = req(page['title'])
            for link in data:
                # check that the page hasn't already been processed
                result = conn.execute("SELECT NAME, PARENT FROM LINKS WHERE NAME=:pageName", {'pageName':link['title']})
                if result.fetchone() is None: 
                    # add a row to the db
                    cursor = conn.cursor()
                    result = cursor.execute("INSERT INTO LINKS (NAME, PARENT) VALUES (:pageName, :parent)", {'pageName':link['title'], 'parent':page['id']})
                    # add the page to the queue
                    print "Adding page to queue: " + link['title']
                    queue.put({'title':link['title'],'id':cursor.lastrowid})
                    continue
                else:
                    print "Already visited page: " + link['title']
                    break;
        except:
            pass
    
try:
    os.remove(r'/tmp/treedb.db')
except:
    pass
conn = sqlite3.connect(r'/tmp/treedb.db')

conn.execute('''CREATE TABLE LINKS
    (NAME TEXT NOT NULL,
    PARENT INT);''')
print "Creating links table"

user    = 'wikigraph69'
passw   = 'hitlersucks69'

baseurl = 'https://en.wikipedia.org/w/api.php'
params  = '?action=login&lgname=%s&lgpassword=%s&format=json'% (user,passw)
 
# Login request
r1 = requests.post(baseurl+params)
token = r1.json()['login']['token']
params2 = params+'&lgtoken=%s'% token
 
# Confirm token; should give "Success"
r2 = requests.post(baseurl+params2,cookies=r1.cookies)

autocomplete("USA")

bfs("Bompas Township, Ontario", None)

parent = conn.cursor().execute("SELECT NAME, PARENT FROM LINKS WHERE NAME=:pageName", {'pageName':'Adolf Hitler'}).fetchone()

print ""
print "Page trace:"

while parent is not None:
    print " + " + parent[0]
    parent = conn.cursor().execute("SELECT NAME, PARENT FROM LINKS WHERE ROWID=:id", {'id':parent[1]}).fetchone()

print ""
print "The end!"
