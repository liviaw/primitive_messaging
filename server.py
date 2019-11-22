# socket_echo_server.py
from socket import *
#from thread_users import thread_func
import time
import threading
import datetime as dt
import sys
from datetime import datetime
from user import *
from afterlogin import messaging
import os

#global variables that are used in multiple files
auth_users = {}
#dictionary of username:userObject
any_users = {}
online_list = []
t_lock=threading.Condition()

server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])
timeout = int(sys.argv[3])

#main function of server
def main():
    global any_users
    global t_lock
    # Create a TCP/IP socket
    setup_auth()
    sock = socket(AF_INET, SOCK_STREAM)  
    # (ip, port)
    server_address = ('0.0.0.0', server_port)
    
    #t_lock = threading.Cond‭ition()
    
    print('>Python3 Server {} {} {}'.format(server_port, block_duration, timeout))
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    
    # Bind the socket to the port
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)
 
    
    #accepting new requests for log in
    while (True):
        # Wait for a connection
        connectionSock, client_address = sock.accept()
        #receive data
        #create thread
        # go to thread_users file
        thread = threading.Thread(target=thread_func, args=(connectionSock, auth_users, block_duration, t_lock, timeout, ))
        thread.daemon = True
        thread.start()
         
            
    return
       
# imports all user details into user objects
def setup_auth():
    f = open("credentials.txt", "r")
    lines = f.readlines()
    for line in lines:
        user, password = line.split()
        auth_users[user] = password
        dummy_user = User (user, password, None)  
        any_users[user] = dummy_user    
    f.close()
    
# create user threads and check if they are authorised to log in
def thread_func(connectionSock, auth_users, block_duration, t_lock, timeout):
    global any_users

    try:    
        data = connectionSock.recv(2048)
    except ConnectionResetError:
        connectionSock.close()
        sys.exit(1)
    # for in case of empty data message such as ctrl - c or null
    except KeyboardInterrupt:
        connectionSock.close()
        os._exit(1)
        return
        
    result = data.decode().split()
     
    # check if the user has logged in yet (maybe in another ip addr)
    try:
        if (result[0] in any_users.keys() and any_users[result[0]].get_login() == True):
            message = "Client already logged in"
            print(message)
            connectionSock.send(message.encode())    
            return
    except IndexError:
        print("Client entered unreadable/invalid data")
        return

    while (True): 
        try:      
            if (result[0] in any_users.keys()):
                # user has been added in before
                # need to update the values
                curr_user = any_users[result[0]]
                curr_user.update(result[0], result[1], connectionSock)               
            else:
                print("Client entered invalid username")
                curr_user = User (result[0], result[1], connectionSock) 
                curr_user.fail_attmp()
        except IndexError:
            continue
            
        any_users[result[0]] = curr_user 
        username = result[0]
        
                   
        # this aldy correct, pls rethink if u wanna change again! T.T
        # you will first go to the first if sttmt no matter what
        ## client logs in!
        if (curr_user.log_in(auth_users, any_users, block_duration) == True):
            time.sleep(1)
            # announce to every logged in users that you have logged in

            print_delay_msg(username, any_users)
            presence_login(any_users, username)  
            messaging(auth_users, any_users, username, timeout)  
            break         
        else:
            try:    
                data = connectionSock.recv(2048)
            except ConnectionResetError:
                connectionSock.close()
                os._exit(1)
            except OSError:
                # make sure user login flag is put as flase
                presence_logout(any_users, username)
                #kill thread
                return
            if (data.decode() == ""):
                return    
            result = data.decode().split()
            # check if the user has logged in yet (maybe in another ip addr)
            if (result[0] in any_users.keys() and any_users[result[0]].get_login() == True):
                message = "Client already logged in"
                connectionSock.send(message.encode())    
                return
      
    # outside while loop

    # at the end of the function, log user out
    presence_logout(any_users, username)
                  
    return
         
# print on terminal messages that were delayed or when the user is offline
def print_delay_msg(username, any_users):
    curr_user = any_users[username]
    while (len(curr_user.messages_queue) != 0):
        connectionSock = curr_user.socket
        message = curr_user.messages_queue.pop(0)
        connectionSock.send(message.encode())

if __name__ == "__main__":
    main()

