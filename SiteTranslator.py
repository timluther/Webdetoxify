#!/usr/bin/env python

import datetime

from colorama import Fore, Back, Style
import os
from http.server import BaseHTTPRequestHandler,HTTPServer
import time
import socket
import logging
import socketserver
import json
import mimetypes
from socketserver import ThreadingMixIn
import io
import requests

HOST, PORT = "0.0.0.0", 8080

verboseLog = False

hostname = socket.gethostname()
LocalIP = socket.gethostbyname(hostname)

def enc(s):
	return bytes(s, 'UTF-8')

	
Messages = []
ServerMap = {}
InteractionMap = {}
ProcessMap = {}
DotoxifyList = [
(enc('brexit') , enc('the tragedy of brexit')),
(enc('Brexit') , enc('the tragedy of Brexit')),
(enc('refugees') , enc('helpless refugees, fleeing death and persecution')),
(enc('Theresa May') , enc('Thereicha Matriarch')),
(enc('Prince Charles') , enc('Unelected figurehead, Prince Charles')),
(enc('Daily Mail') , enc('Daily Flail')),
(enc('MAILONLINE') , enc('FAILONLINE')),
(enc('Enter your search') , enc('Pit of despair')),
(enc('Remoaners'), enc('Rational remainers')),
(enc('DON\'T MISS</h3>') , enc('SIDEBAR OF SHAME</h3>')),
(enc('News</a>'), enc('So Called News</a>')),
(enc('<li>TRENDING:</li>'), enc("<li>IT'S ALL LIES</li>")),
(enc('Daily Express'), enc("Daily Excess")),
(enc('<a href="/horoscope">Daily<br>Horoscope</a>'), enc('<a href="http://rationalsciencemethod.blogspot.co.uk/2012/12/the-rational-scientific-method.html">Horoscopes are superstitious nonsense</a>'))
]

StaticWebPageMap = {}

def safe_map_inc(map, key, amount = 1):	
	if map.get(key) == None:
		map[key] = amount
	else:
		map[key] += amount


def get_webpage(url, headers):	
	print("Grabbing url: " + url)
	response = requests.get(url) #, headers=headers)
	print(dir(response))
	print(response.headers)
	
	return response.content, response.headers['content-type']

def translate_and_cache(map, path, headers):
	#time = os.path.getmtime(fname)
    entry = map.get(path)
    #or entry[2] < time:
    if entry == None:
        page, content_type = get_webpage(path, headers)
        #print(page)
        #todo translate here
        if content_type.find('text/html') != -1:
        	for value in DotoxifyList:
        		page = page.replace(value[0], value[1])
        map[path] = (page, 'text/html', 0.0)
        #static_page_lock.release()
        return map[path]
    else:
        return entry


currentSite = ''
ErrorPageHeader = enc("<html><head><title>Error</title></head><body><h1>ServerError</h1><p>")
ErrorPageFooter = enc("</p></body></html>")
#server_list_HTML_cache = CachedGeneratedPage(writeServerInfoHTML)
# This class will handle any incoming request from
# a browser 
class webHandler(BaseHTTPRequestHandler):

					
	def doCachedResource(self, path, headers):
		self.send_response(200)
		global currentSite
		#if os.path.isabs(self.path):
		#	print("Absolute path provided, dropping: " + self.path)					
		#else:									
		try:
			path = path.strip("\\/")
			http_idx = path.find('http://')
			if http_idx != -1:
				currentSiteNameEndIdx = path.find("/", http_idx+7)
				if currentSiteNameEndIdx != -1:				
					currentSite = path[:currentSiteNameEndIdx+1]
				else:
					currentSite = path
				print("Current site: " + currentSite)
				if currentSite.endswith('/') == False:
					currentSite = currentSite + "/"
				print("Current site: " + currentSite)
			else:
				path = currentSite + path
			#path = os.path.join(basedir, path.strip("\\/"))	
			
			page, mime, time = translate_and_cache(StaticWebPageMap, path, headers)
			print(Fore.MAGENTA + " Serving content with following mime type: " + str(mime))
			self.send_header('Content-type',mime)
			self.end_headers()
			self.wfile.write(page)
		except Exception as e:
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(ErrorPageHeader)
			self.wfile.write(enc('Server Error processing: ' + path + ", " + str(e)))
			self.wfile.write(ErrorPageFooter)
			

	def do_POST(self):
		return
	# Handler for the GET requests
	def do_GET(self):
		global basedir
		print   ('Get request received')
		#referer = self.headers.get('Referer')
		#print("The referer is", referer)
		path = self.path
		print(Fore.MAGENTA + "HTTP get request: " + path + Style.RESET_ALL)		
		
		# Send the html message
		self.doCachedResource(path, self.headers)			
				
		return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

if __name__ == "__main__":	
	print("Website detoxifier on port " + str(PORT))
	try:
		httpserver =ThreadedHTTPServer((LocalIP, PORT), webHandler)

		httpserver.serve_forever()
		# Wait forever for incoming http requests
		

	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:

		print ("Crtl+C Pressed. Shutting down.")
	
	print("Finished.")

		