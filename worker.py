#-----------------------------------------
# NAME: Hasin Ishrak 
# STUDENT NUMBER: 7886741
# COURSE: COMP 3010, SECTION: A02
# INSTRUCTOR: Dr. Sara Rouhani
# TERM: FALL 2023
# ASSIGNMENT: Assignment 02
# 
# REMARKS: Creting a workers to work for the webserver/coordinator.
#
#--------> All the tweets are stored in the data_store array
#
# Note that: there are already two pre-loaded tweets
#-----------------------------------------


import socket
import threading
import json
import sys

# Global data store for this worker
data_store = [
    {
        'id': "tweet_01",
        'name': "John",
        'msg': "This is John",
        'isBlocked': "No"
    },
    {
        'id': "tweet_02",
        'name': "Mike",
        'msg': "This is Mike",
        'isBlocked': "No"
    }

]

# Function to handle incoming messages
def handle_message(client_socket):
    message = client_socket.recv(1024).decode('utf-8')
    message_data = json.loads(message)

    if message_data['method'] == 'get':
        client_socket.send(json.dumps(data_store).encode('utf-8'))
        print(f'Worker -> API list sent!')
    elif message_data['action'] == 'vote':
        id = message_data['id']
        tweet = None
        for data in data_store:
            if (data['id'] == id):
                tweet = data
        if (tweet == None):
                tweet = {'id': message_data['id'], 'name': "", 'msg': "", 'isBlocked': ""}
                data_store.append(tweet)

        if (tweet["isBlocked"] == "Yes"):
            client_socket.send("Busy".encode('utf-8'))
            print(f'Worker ->Can not Proceed to commit!')
        else:
            tweet["isBlocked"] = "Yes"
            client_socket.send("commit".encode('utf-8'))
            print(f'Worker ->Proceed to commit!')
    elif message_data['action'] == 'commit' and message_data['method'] == 'DELETE':
        id = message_data['id']
        tweet = None
        for data in data_store:
            if (data['id'] == id):
                tweet = data
        data_store.remove(tweet)
        client_socket.send("done".encode('utf-8'))
        print(f'Worker -> Tweet Deleted!')
    elif message_data['action'] == 'commit':
        id = message_data['id']
        tweet = None
        for data in data_store:
            if (data['id'] == id):
                tweet = data
        tweet["name"] = message_data['name']
        tweet["msg"] = message_data['msg']
        tweet["isBlocked"] = "No"
        client_socket.send("done".encode('utf-8'))
        print(f'Worker -> Tweet Updated!')

    
# Worker function
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = int(sys.argv[1])
    server.bind(('localhost', port))  # Change port for each worker
    server.listen(5)
    print(f'\n  ---> Worker is listening on port: {port}\n')
    
    while True:
        client, addr = server.accept()
        print(f'Accepted connection from {addr[0]}:{addr[1]}')
        client_handler = threading.Thread(target=handle_message, args=(client,))
        client_handler.start()

if __name__ == '__main__':
    main()
