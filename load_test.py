#-----------------------------------------
# NAME: Hasin Ishrak 
# STUDENT NUMBER: 7886741
# COURSE: COMP 3010, SECTION: A02
# INSTRUCTOR: Dr. Sara Rouhani
# TERM: FALL 2023
# ASSIGNMENT: assignment 02, PART: Load test
# 
# REMARKS: Creting a multi-threaded client
#           that makes request for 30 new tweets
#           and also makes another request to get
#           all the tweets. [Load test]
#
#-----------------------------------------


import socket
import threading
import time

# Define the server's host and port
server_host = 'goose.cs.umanitoba.ca'
server_port = 8357

# Function to make new_tweet request
def make_request():
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Connect to the server
        client_socket.connect((server_host, server_port))

        request = f"POST /api/tweet HTTP/1.1\r\nHost: {server_host}\r\nCookie: name=Rob\r\n\r\nmsg=Good day"

        # Send the request
        client_socket.send(request.encode('utf-8'))


        time.sleep(0.2)
        # Close the socket
        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")
        return
    

# Function to make get_all_tweets request
def make_request_2():
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Connect to the server
        client_socket.connect((server_host, server_port))

        request = f"GET /api/tweet HTTP/1.1\r\nHost: {server_host}\r\nCookie: name=Rob\r\n\r\n"

        # Send the request
        client_socket.send(request.encode('utf-8'))

        recv = client_socket.recv(4096)
        recv = recv.decode('utf-8')
        print(recv)


        time.sleep(0.2)
        # Close the socket
        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")
        return

# Create 100 threads to make the requests
threads = []
for _ in range(30):
    thread = threading.Thread(target=make_request)
    threads.append(thread)
    thread.start()

# Wait for all threads to finish
for thread in threads:
    thread.join()

# Now get all the tweets
thread = threading.Thread(target=make_request_2)
thread.start()
thread.join()

print("All requests have been sent.")
