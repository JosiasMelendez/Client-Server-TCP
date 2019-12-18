# Josias Melendez
# UCID: jjm72
# Section 102
# References TCP Client API
# If you delete cache.txt in order to emulate no cache, please also delete cachedfile.txt
# This was the only way I could figure out how to remember the name of the file in cache
# without modifying the file in cache itself

import sys, datetime, time
import os.path
from socket import *

# Get the url containing hostname, server port, and file name
argv = sys.argv
url = argv[1]

# Find hostname, port, and file name in the argument
urlparts = url.split(':')
hostname = urlparts[0]
portfile = urlparts[1].split('/')
port = int(portfile[0])
filename = "/" + portfile[1]

# Build first part of message
message = "GET " + filename + " HTTP/1.1\r\n" + "Host: " + hostname + ":" + str(port) + "\r\n"

# Check if cache exists and what file is in cache
try:
    file = open('cachedfile.txt', "r")
    linelist = file.readlines()
    if (filename == linelist[0]):
        newfile = False
        # Only use conditional GET if file is not in the cache
        modtime_secs = os.path.getmtime('cache.txt')
        modtime_tup = time.gmtime(modtime_secs)
        modtime_http = time.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n", modtime_tup)
        message += "If-Modified-Since: " + modtime_http + "\r\n"
    else:
        newfile = True
except FileNotFoundError:
    newfile = True
    message += "\r\n"

print(message)
# Resolve the hostname
ip = gethostbyname(hostname)

# Create socket.
clientSocket = socket(AF_INET, SOCK_STREAM)

# Create connection and send
clientSocket.connect((ip, port))
clientSocket.send(message.encode())

# Receive the server response
response = clientSocket.recv(10000)
httpresponse = response.decode()

# Find needed parts of response
httpresponses = httpresponse.split('\r\n')
fileindex = len(httpresponses) - 1
recvfile = httpresponses[fileindex]
status = httpresponses[0]

# Output based on response
if (status == "HTTP/1.1 200 OK"):
    if (newfile == False):
        print("File has been modified since last retrieved.")
    else:
        # To know what file is in the cache, use a separate file to hold file name
        file = open("cachedfile.txt", "w")
        file.write(filename)
    f = open("cache.txt", "w")
    f.write(recvfile)
    f.close()
print(httpresponse)

# Close the client socket
clientSocket.close()
