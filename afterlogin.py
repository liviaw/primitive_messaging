from user import *
from socket import *
from datetime import datetime
import time
import threading
import datetime as dt
import sys
import os
from command_functions import block, unblock, broadcast, msg, whoelse, whoelsesince, presence_login, presence_logout, start_private

#update, fail_attmp. failed_log_in_3_times, 
def messaging (auth_users, any_users, username, timeout):
    connectionSock = any_users[username].socket
    curr_user = any_users[username]
    timer = threading.Timer(timeout, presence_logout, (any_users, username))
    print(">Server starts timer for client " + username)
    timer.start()
    while (True):
        try:
            data = connectionSock.recv(2048).decode()
            if (data == ""):
                continue
            timer.cancel()  
            print("receiving")        
            curr_user.set_time(time.time())             
        except ConnectionResetError:
            connectionSock.close()
            return
            sys.exit()
        except OSError:
            #kill thread
            print(">Bye-bye! Stopping programe...")
            presence_logout(any_users, username)
            return
            #sys.exit()
        result = data.split()
       
        if (result[0] == 'logout'):
            print(">" + username + " wants to logout")
            presence_logout(any_users, username)
            return
        elif (data == "whoelse"):
            whoelse(any_users, username)    
        elif (len(result) > 0):
            if (result[0] == "message"):
                msg(auth_users, any_users, username, result)
            elif (result[0] == "broadcast"):
                broadcast(any_users, curr_user, result)
            elif (result[0] == "whoelsesince"):
                whoelsesince (username, any_users, result)
            elif (result[0] == "block"):
                block(curr_user, result)
            elif (result[0] == "unblock"):
                unblock (curr_user, result)
            #elif (result[0] == "sock"):
            #    print(curr_user.socket)
            elif (result[0] == "startprivate"):
            
                start_private(username, result, any_users, auth_users)
                
                # Client A wants to connect to client B
                # Client A creates a server and listens
                # Server tells client B of client A's address
                # Client B connects to client A using the given address
            else:
                print(">Error. More than one string received")
                message = ">Error. Invalid command"
                connectionSock.send(message.encode())
        else:
            message = ">Error. Invalid command"
            print(">Error. caught.")
            connectionSock.send(message.encode())
        if data != "":    
            timer = threading.Timer(timeout, presence_logout, (any_users, username))
            timer.start() 
            



