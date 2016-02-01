#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #returns host, port, path
    def get_host_port(self,url):
        #print("url: %s"% url)
        urllist = url.split(":")
        #print("urllist: %s" % urllist)

        #doesn't have a specific port
        if (len(urllist) == 2):
            hostlist = urllist[1].strip('/').split("/")
            port = 80
            host = hostlist[0].strip('/')
            hostlist.pop(0)
        #has a specific port
        else:
            #print("here")
            hostlist = urllist[2].strip('/').split("/")
            port = hostlist[0]
            hostlist.pop(0)
            host = urllist[1].strip('/')
        #print("port: %s" %port)

        #print("hostlist: %s" %hostlist)
        #print("host: %s" % host)
        #get path
        path = ""
        for i in range(0,len(hostlist)):
            path += "/"
            path += hostlist[i]
        if (path==""):
            path += "/"
        #print("path: %s" % path)

        return host, port, path

    def connect(self, host, port):
        # use sockets!
        #print("%s,%s" %(host,port))
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((host,port))
        #print ("connected!")
        return clientSocket

    def get_code(self, data):
        datalist = data.split("\r\n\r\n")
        header = datalist[0]
        code = int(header.split()[1])
        #print("code: %s" %code)
        return int(code)

    def get_headers(self,data):
        datalist = data.split("\r\n\r\n")
        header = datalist[0]
        return header

    def get_body(self, data):
        datalist = data.split("\r\n\r\n")
        body = datalist[1]
        return body

    def get_args(self, data):
        datalist = data.split("\r\n\r\n")
        body = datalist[1]
        #print("body in args: %s" %body)
        return body

    # read everything from the socket
    def recvall(self, sock):
        response = bytearray()
        done = False
        while True:
            part = sock.recv(1024)
            if (part):
                response.extend(part)
            else:
                break
        return str(response)

    def GET(self, url, args=None):
        #need to get host, port, path from url
        host, port, path = self.get_host_port(url)
        #convert args to url encoding
        if (args != None):
            argstring = urllib.urlencode(args)
        else: 
            argstring = ""
        #GET / HTTP/1.1\r\nHost: host:port\r\nConnection: close\r\n\r\n
        request = "GET %s HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % (path,host)
        request += argstring
        request += "\r\n\r\n"
        #print("request: %s" %request)
        clientSocket = self.connect(host, int(port))
        clientSocket.sendall(request)
        response = self.recvall(clientSocket)
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        clientSocket.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = self.get_host_port(url)
        #convert args to url encoding
        if (args != None):
            argstring = urllib.urlencode(args)
        else: 
            argstring = ""
        #print("argstring: %s" %argstring)
        request = "POST %s HTTP/1.1\r\nHost: %s\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %s\r\nConnection: close\r\n\r\n" % (path,host,len(argstring))
        request += argstring
        request += "\r\n\r\n"
        #print("request: %s" %request)
        clientSocket = self.connect(host, int(port))
        clientSocket.sendall(request)
        response = self.recvall(clientSocket)
        print(response)
        code = self.get_code(response)
        body = self.get_body(response)
        clientSocket.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    #fixed by Victor Olivares
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        #user command
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        #GET
        print client.command( sys.argv[1] )