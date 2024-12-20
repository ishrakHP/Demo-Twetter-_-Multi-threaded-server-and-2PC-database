#-----------------------------------------
# NAME: Hasin Ishrak 
# STUDENT NUMBER: 7886741
# COURSE: COMP 3010, SECTION: A02
# INSTRUCTOR: Dr. Sara Rouhani
# TERM: FALL 2023
# ASSIGNMENT: Assignment 02
# 
# REMARKS: Creting a multi-threaded web server
#          called ELK
#
#--------> In my case, I do not have a coordinator.
#          My webserver is the cooridinator.
#          It is non-bloking using threading.
#          No data is stored here in the server, except the addresses of the worker(s).
#
#-----------------------------------------



# Imports
#________

import socket
import sys
import os
import time
import datetime
import pytz
import threading
import json
import uuid
import random


# Global Variables
#_________________
worker_addresses = [('localhost', 8355), ('localhost', 8359)]                # addresses of the worker(s).
timeout_seconds = 1


# Work for a single worker ->  Fetching.
# index determines which worker to choose which is done by round-robin using random
#__________________________________________________________________________________
def send_to_a_worker(index, message):
    msg = ""
    worker_address = worker_addresses[index]
    worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    worker_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    worker_socket.connect(worker_address)
    try:
        worker_socket.send(message.encode('utf-8'))
        msg = worker_socket.recv(4096)
    except Exception as e:
        print(e)
    worker_socket.close()
    return msg


# Creating a dictionary to map file extensions
#_____________________________________________

content_types = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.json': 'application/json',
    '.txt': 'text/plain',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.js': 'application/javascript',
    '.pdf': 'application/pdf',
    '.json': 'application/json',
}




# Functions/ Method
#__________________

def parse_http_request(request):
    
    parsed_data = {}
    
    try:
        if '\r\n\r\n' in request:
            headers, body = request.split('\r\n\r\n', 1)
        else:
            headers = request
            body = ''

        method, file_path, _ = headers.split(' ', 2)

        parsed_data['method'] = method
        parsed_data['file_path'] = file_path
        
        header_lines = headers.split('\r\n')[1:]
        for line in header_lines:
            key, value = line.split(': ', 1)
            parsed_data[key] = value

        if method == 'POST' or method == 'PUT':
            parsed_body = body.split('&')
            for item in parsed_body:
                key, value = item.split('=', 1)
                parsed_data[key] = value

    except Exception as e:
        print("Could not parse the HTTP request because of ->", str(e))
        return 400

    return parsed_data


def round_robin():
    num_of_worker = len(worker_addresses)
    worker = random.randint(0, num_of_worker-1)
    return worker



def get_content_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    return content_types.get(file_extension.lower(), 'text/plain')



def get_api_tweet():
    message = json.dumps({'method': 'get', 'action': 'None'})
    worker = round_robin()
    recv = send_to_a_worker(worker, message)
    recv = recv.decode('utf-8')
    return recv

# Implements 2PC algorithm for writes
# Time-out is set to 1 sec
#_____________________________________
def set_api_tweet(id, name, msg, method):
    message = json.dumps({'method': method, 'action': 'vote', 'id': str(id)})
    number_of_worker = len(worker_addresses)
    count = 0
    for i in range(0, number_of_worker):
        start_time = time.time()
        while True:
            recv = send_to_a_worker(i, message).decode('utf-8')
            if(recv) == "commit":
                count += 1
                break
            current_time = time.time()
            if (current_time - start_time >= timeout_seconds):
                break
    message = json.dumps({'method': method, 'action': 'commit', 'name': name, 'id': str(id),'msg': msg})
    if count == number_of_worker:
        count = 0
        for i in range(0, number_of_worker):
            start_time = time.time()
            while True:
                recv = send_to_a_worker(i, message).decode('utf-8')
                if(recv) == "done":
                    count += 1
                    break
                current_time = time.time()
                if (current_time - start_time >= timeout_seconds):
                    break
    else:
        return "failed"
    
    if (count == number_of_worker):
        return "success"
    else:
        return "failed"





def work(client_connection, client_address):
    
    with client_connection:

        try:
            print(f'\n    Connection established from {client_address}\n')

            # Receiving client requests
            client_request = client_connection.recv(1024)

            data = client_request.decode('utf-8')

        except Exception as e:
            print("-----------No Data Received!!!---------------------")
            print(e)
            return


        # Return status variable
        status_code = 0
        content_type = ''
        last_modified = ''
        server_name = 'COMP3010_A2_WEBSERver'


        # print("data -> " + data)
        http_req = parse_http_request(data)

        
        # If the request is not in the correct order send 400 Bad Request
        if (http_req == 400):
            status_code = 400
            send_data = f"HTTP/1.1 {status_code} Bad Request\r\n\r\n"
            send_data = send_data.encode('utf-16')
            client_connection.sendall(send_data)
            return

        # If the request is not for GET or POST, send 400 Bad Request
        if (http_req['method'] != 'GET' and http_req['method'] != 'POST' and http_req['method'] != 'PUT' and http_req['method'] != 'DELETE'):
            status_code = 400
            send_data = f"HTTP/1.1 {status_code} Bad Request\r\n\r\n"
            send_data = send_data.encode('utf-8')
            client_connection.sendall(send_data)
        else:
            if (http_req['file_path'] == '/' or http_req['file_path'] == '/index.html') :

                file_path = "index.html"
                status_code = 200
                content_type = get_content_type(file_path)
                content_length = -1
                
                lastUpdatedPattern = "%a, %d %b %Y %H:%M:%S %Z"
                modifiedTimestamp = os.path.getmtime(file_path)
                modifiedTime = datetime.datetime.fromtimestamp(modifiedTimestamp, tz=pytz.timezone("America/Winnipeg"))
                last_modified = modifiedTime.strftime(lastUpdatedPattern)

                try:
                    with open('index.html', 'r') as file:
                        content = file.read()
                        content_length = str(len(content))
                        send_data = (f"HTTP/1.1 {status_code} OK\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nLast-Modified: {last_modified}\r\nServer: {server_name}\r\n\r\n" + content)
                except FileNotFoundError as e:
                    send_data = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
                    print(e)


            elif (http_req['method'] == 'POST' and http_req['file_path'] == '/api/login'):
                if (http_req.get('name')):
                    set_cookie = "name=" + http_req.get('name')
                    status_code = 200

                    send_data = (f"HTTP/1.1 {status_code} OK\r\nSet-Cookie: {set_cookie}\r\nServer: {server_name}\r\n\r\n")
                else:
                    send_data = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"


            elif (http_req['method'] == 'DELETE' and http_req['file_path'] == '/api/login'):
                if (http_req.get("Cookie") != None):
                    _, name = http_req.get('Cookie').split('=', 1)
                    set_cookie = "name=" + name + "; expires=Thu, 01 Jan 1970 00:00:00 GMT;"
                    status_code = 200

                    send_data = (f"HTTP/1.1 {status_code} OK\r\nSet-Cookie: {set_cookie}\r\nServer: {server_name}\r\n\r\n")
                else:
                    send_data = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"


            elif (http_req['method'] == 'GET' and http_req['file_path'] == '/api/tweet'):
                if (http_req.get("Cookie") != None):
                    content = get_api_tweet()
                    if(content != ""):
                        status_code = 200
                        content_type = "application/json"
                        content_length = str(len(content))
                        send_data = (f"HTTP/1.1 {status_code} OK\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\nLast-Modified: {last_modified}\r\nServer: {server_name}\r\n\r\n" + content)
                    else:
                        send_data = (f"HTTP/1.1 502 Bad Gateway\r\nServer: {server_name}\r\n\r\n")
                else:
                    send_data = "HTTP/1.1 401 Unauthorized\r\n\r\nFile Not Found"


            elif (http_req['method'] == 'POST' and http_req['file_path'] == '/api/tweet'):
                if (http_req.get("Cookie") != None):
                    _, name = http_req.get('Cookie').split('=', 1)
                    if (set_api_tweet("tweet_"+ str(uuid.uuid1()), name, http_req.get('msg'), http_req['method']) == "success"):
                        status_code = 200
                        send_data = (f"HTTP/1.1 {status_code} OK\r\nServer: {server_name}\r\n\r\n")
                    else:
                        send_data = (f"HTTP/1.1 502 Bad Gateway\r\nServer: {server_name}\r\n\r\n")
                else:
                    send_data = "HTTP/1.1 401 Unauthorized\r\n\r\nFile Not Found"


            elif (http_req['method'] == 'PUT'):
                if (http_req.get("Cookie") != None):
                    _, id = http_req['file_path'].rsplit('/api/tweet/', 1)
                    msg = http_req['msg'].split('said ', 1)
                    if len(msg) >1:
                        msg = msg[1]
                    else:
                        msg = http_req['msg']
                    _, name = http_req.get('Cookie').split('=', 1)
                    if (set_api_tweet(id, name, msg, http_req['method']) == "success"):
                        status_code = 200
                        send_data = (f"HTTP/1.1 {status_code} OK\r\nServer: {server_name}\r\n\r\n")
                    else:
                        send_data = (f"HTTP/1.1 502 Bad Gateway\r\nServer: {server_name}\r\n\r\n")
                else:
                    send_data = "HTTP/1.1 401 Unauthorized\r\n\r\nFile Not Found"


            elif (http_req['method'] == 'DELETE'):
                if (http_req.get("Cookie") != None):
                    _, id = http_req['file_path'].rsplit('/api/tweet/', 1)
                    _, name = http_req.get('Cookie').split('=', 1)
                    if (set_api_tweet(id, name, "", http_req['method']) == "success"):
                        status_code = 200
                        send_data = (f"HTTP/1.1 {status_code} OK\r\nServer: {server_name}\r\n\r\n")
                    else:
                        send_data = (f"HTTP/1.1 502 Bad Gateway\r\nServer: {server_name}\r\n\r\n")
                else:
                    send_data = "HTTP/1.1 401 Unauthorized\r\n\r\nFile Not Found"
                

            else:
                send_data = "HTTP/1.1 404 Not Found\r\n\r\nPage Not Found"

            
            try:
                client_connection.sendall(send_data.encode('utf-8'))
            except IOError as e:
                print("Data sending Error: -> " + e) 

        print(f"        Respose sent!")


# Main
#______

def main():

    # Check for the correct number of arguments
    num_of_args = len(sys.argv)
    if (num_of_args < 2):
        print(f'    ---> Not enough command-line arguments !!!')
        exit()


    # Creating Socket
    HOST_NAME = socket.gethostname()
    SERVER_HOST = socket.gethostbyname(HOST_NAME)
    SERVER_PORT = int(sys.argv[1])

    webserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    webserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    webserver.bind((SERVER_HOST, SERVER_PORT))


    # Starting the server
    webserver.listen()
    print(f'\n  ---> Web server is listening on port: {SERVER_PORT}\n')
    

    # Keeping the server alive
    while True:
       
        try:
            client_connection, client_address = webserver.accept()
            thread = threading.Thread(target=work, args=(client_connection, client_address))
            thread.start()
        except Exception as e:
            print(f"Error accepting client connection: {e}")



if __name__ == '__main__':
    main()

