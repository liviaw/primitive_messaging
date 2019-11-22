from user import *
from datetime import datetime
import time
import threading
import datetime as dt
import sys
import os

#blacklist user                
def block (curr_user, result):
    connectionSock = curr_user.socket
    message = ""
    if (len(result) < 2):
        message = ">Error. Enter block user"
    elif (result[1] == curr_user.username):
        message = ">Error. Cannot block self"
    elif (result[1] in curr_user.block):
        message = ">User " + result[1] + " is still under blocked condition"
    else:      
        curr_user.block.append(result[1])
        message =  ">" + curr_user.username + " is blocking " + result[1]
    connectionSock.send(message.encode())
    
#remove user from blacklist    
def unblock (curr_user, result):
    connectionSock = curr_user.socket
    if (len(result) < 2):
        message = ">Error. Enter unblock user"
        connectionSock.send(message.encode())
    elif (result[1] == curr_user.username):
        message = ">Error. Cannot unblock self"
        connectionSock.send(message.encode())
    elif (result[1] not in curr_user.block):
        message = ">Error. " + result[1] + " was not blocked"
        connectionSock.send(message.encode())
    else:
        curr_user.block.remove(result[1])
        connectionSock = curr_user.socket
        message = curr_user.username + " is unblocking " + result[1]
        connectionSock.send(message.encode())
#send the same message to every user            
def broadcast (any_users, curr_user, result):  
    if (len(result) < 2):
        message = ">Error. Enter broadcast message"
        connectionSock.send(message.encode())  
        return
    username = curr_user.username
    message = ">" + username + ": "
    i = 1
    while (i < len(result)):
        message = message + " " + result[i]
        i = i + 1
    block_flag = False    
    for receiver in any_users:
        if (curr_user not in any_users[receiver].block):
            if (curr_user != any_users[receiver] and any_users[receiver].get_login() == True):
                rec_socket = any_users[receiver].socket
                rec_socket.send(message.encode())
                print(">Print broadcasting")
        else:
            block_flag = True

    if (block_flag == True):
        connectionSock = curr_user.socket
        message = ">Your message could not be delivered to some recipients"
        connectionSock.send(message.encode())

#message between users, with the help of server         
def msg (auth_users, any_users, username, result):
    
    curr_user = any_users[username]
    connectionSock = curr_user.socket
    if (len(result) < 3):
        message = ">Error. Enter [message] [receiver] [message]...[message]"
        connectionSock.send(message.encode())  
        return
    elif (result[1] not in auth_users.keys()):
        message = ">User does not exist in credential file"
        connectionSock.send(message.encode())
    elif (username == result[1]):
        message = ">Can't message self"
        connectionSock.send(message.encode())
        return
    else:    
        receiver = any_users[result[1]]
        message = ">" + username + ":" 
        i = 2
        while (i < len(result)):
            message = message + " " + result[i] 
            i = i + 1
        message = message + "\n"
        if (receiver.login == False):
            #have logged in before but currently logged out     
            receiver.messages_queue.append(message)
        else:        
           
            if (username not in receiver.block):
                rec_socket = receiver.socket
                rec_socket.send(message.encode())
            else:            
                message = ">Your message could not be delivered as the recipient has blocked you"
                connectionSock.send(message.encode())

# list down people who are currently logged in     
def whoelse(any_users, username):
    online_users = "=== Who is currently online ===\n"
    for u in any_users.keys():
        if (username != u and any_users[u].get_login() == True):
            online_users = online_users + ">" + u + "\n"
        
    connectionSock = any_users[username].socket
    connectionSock.send(online_users.encode())
    
#who are the users that logged in the past <time> second
def whoelsesince (username, any_users, result):
    connectionSock = any_users[username].socket
    if (len(result) < 2):
        message = ">Please enter time range"
        connectionSock.send(message.encode())
        return
    try:
        time_str = int(result[1])
    except ValueError:
        message = ">Please give time in type integer"
        connectionSock.send(message.encode())
        return
    now = time.time()
    online_since = "=== who was online from " + result[1] + " ago ===\n"
    for user in any_users:
        if (any_users[user].username == username):
            continue
        u = any_users[user]
        if u.get_login() == True:
            online_since = online_since + ">" + u.username + "\n"
            continue
        for onl in u.online:
            if (onl >= (now-time_str)):
                online_since = online_since + ">" + any_users[user].username + "\n"
                #break the inner loop and go to the next user
                break 
        
    connectionSock.send(online_since.encode())
    
    
# tell everyone that you are logged in    
def presence_login(any_users, username):
    
    data =  username + " logged in"
    
    for user in any_users:
        if (username != user and any_users[user].get_login() == True and username not in any_users[user].block):
            connectionSock = any_users[user].socket
            if (connectionSock != None):
                connectionSock.send(data.encode())
    return True
          
# inform every logged in user that this user has logged out
def presence_logout(any_users, username):
    if ((username in any_users.keys()) and (any_users[username].get_login() == True)):
        print(">Sever printing presence log out")
        data =  username + " logged out"
        for user in any_users:
            if (username != user and any_users[user].get_login() == True and username not in any_users[user].block):
                connectionSock = any_users[user].socket
                if (connectionSock != None):
                    connectionSock.send(data.encode())
                
        connectionSock = any_users[username].socket
        message = "logout"
        print(">Sever send logout message to client")
        connectionSock.send(message.encode()) 
        connectionSock.close() 
        any_users[username].log_out()
        #del any_users[username]

#for the purposes of transforming a tuple into a string
def tupleToDelimString(tup):
    return "|".join([str(item) for item in tup])

# checks if initiator is able to connect to the receiver    
def start_private(sender_name, result, any_users, auth_users):
    message = ""
    connectionSock = any_users[sender_name].socket
    if (len(result) != 2):    
        message = ">Please enter [startprivate] [username]"        
        connectionSock.send(message.encode())
        return
    receiver_name = result[1]
    # user is invalid
    if receiver_name not in auth_users.keys():
        message = ">Error. Invalid user"
        connectionSock.send(message.encode())
        return
    # user is offline / not connected to the server
    elif any_users[receiver_name].get_login() == False:
        message = ">Error. User is offline" 
        connectionSock.send(message.encode())
        return
    # user has been blocked
    elif receiver_name in any_users[receiver_name].block:
        message = ">Cannot start private message as the recipient has blocked you"
        connectionSock.send(message.encode())
        return
    # user is self
    elif sender_name == receiver_name:
        message = ">Error. Cannot start private self"
        connectionSock.send(message.encode())
        return

    message = "start p2p"
        
    # Send a message to the initiator to start listening on their P2P socket
    # (Create socket if necessary)
    connectionSock.send(message.encode())
    time.sleep(0.5)
    #init_addr_string = connectionSock.recv(2048).decode()
       
    # Get both the ip and port of the initiator
    # --> Send this to the receiver
    # --> When receiver gets the ip and port of the initiator, connect to that
    receiverSock = any_users[receiver_name].socket
    initiator_addr = connectionSock.getpeername()
    init_addr_string = tupleToDelimString(initiator_addr)
    
    
    data = "connect p2p initiator " + sender_name + " " + init_addr_string + " " + receiver_name
    receiverSock.send(data.encode())
    time.sleep(1)
    
    received_msg = connectionSock.recv(2048).decode()
    if (received_msg == "succeed"):
        print(">Start " + sender_name + " private messaging with " + receviver_name)
 
