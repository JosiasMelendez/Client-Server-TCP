# Josias Melendez
# UCID: jjm72
# Section 102
# References TCP Server API

import sys, datetime, time, os.path
from socket import *
argv = sys.argv
ip = argv[1]
port = int(argv[2])
dataLen = 100000

# Create socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((ip, port))

# Listen for incoming requests
serverSocket.listen(1)
print("Server is listening")

# Loop forever listening for incoming connection requests on socket
while True:
    # Accept connection requests, create new socket for data
    connectionSocket, address = serverSocket.accept()
    message = connectionSocket.recv(dataLen).decode()
    # Find request type
    request = message.split("\r\n")
    requestline = request[0].split(" ")
    filename_slash = requestline[1]
    filename = filename_slash.replace("/", "")
    # Default starting line
    response = "HTTP/1.1 200 OK\r\n"

    # Check if file exists
    try:
        file_seconds = os.path.getmtime(filename)
        file_tup = time.gmtime(file_seconds)
        file_http = time.strftime("%a, %d %b %Y %H:%M:%S GMT", file_tup)
        file_time = time.strptime(file_http, "%a, %d %b %Y %H:%M:%S %Z")
        seconds_file = time.mktime(file_time)
        notfound = False
    except FileNotFoundError:
        notfound = True
        response = "HTTP/1.1 404 Not Found\r\n"

    # Find current date
    current_time = time.gmtime()
    current_datetime = "Date: " + time.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n", current_time)
    
    # Check modification dates
    if (any("If-Modified-Since" in header for header in request) and (notfound == False)):
        # Find time sent to server
        modified_header = [header for header in request if "If-Modified-Since" in header]
        modify_header = modified_header[0]
        modify_time = modify_header.split(": ")
        modified_time = modify_time[1]
        # Convert time to seconds
        t = time.strptime(modified_time, "%a, %d %b %Y %H:%M:%S %Z")
        seconds_request = time.mktime(t)
        if (seconds_file > seconds_request):
            modified = True
        else:
            modified = False

        # Determine response based on modification time
        if (modified):
            response = "HTTP/1.1 200 OK\r\n"
        else:
            response = "HTTP/1.1 304 Not Modified\r\n"
    
    # Add current date and time to response
    response += current_datetime
    firstline = response.split("\r\n")[0]
    # Build headers for OK response
    if (firstline == "HTTP/1.1 200 OK"):

        # Get last modified time
        filetime = os.path.getmtime(filename)
        filetime_modified = time.gmtime(filetime)
        filetime_modified_http = time.strftime("%a, %d %b %Y %H:%M:%S GMT\r\n", filetime_modified)
        response += ("Last-Modified: " + filetime_modified_http)

        # Get size of file
        fileinfo = os.stat(filename)
        filesize = fileinfo.st_size
        response += ("Content-Length: " + str(filesize) + "\r\n")
        response += "Content-Type: text/html; charset=UTF-8\r\n"

    # Add last \r\n
    response += "\r\n"

    # Back to OK response to add file contents
    if (firstline == "HTTP/1.1 200 OK"):
        f = open(filename, 'r')
        file_contents = f.read()
        response += file_contents
    # Send back to client
    connectionSocket.send(response.encode())
    connectionSocket.close()
