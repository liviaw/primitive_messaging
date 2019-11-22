from socket import *
import time
import threading
import datetime as dt
import sys
from datetime import datetime
from command_functions import block, unblock, broadcast, msg, whoelse, whoelsesince, presence_login, presence_logout
class User:

    def __init__(self, username, password, connectionSock):
        self.username = username
        self.password = password
        self.login = False
        self.num_fails = 1
        self.last_online =  -1
        self.block = []
        # list of times user online
        self.online = []
        self.messages_queue = []
        self.socket = connectionSock

        
    #update user details when client log in
    def update(self, username, password, connectionSock):
        self.username = username
        self.password = password
        self.login = False
        self.socket = connectionSock
        
    # increment fail attempt     
    def fail_attmp(self):
        self.num_fails = self.num_fails + 1        
    
    # check if user has failed to log in 3 times or more   
    def failed_log_in_3_times(self):
        if (self.num_fails <= 3):
            return True
        return False
    # reset fail attempt counter    
    def reset_attmp(self):
        self.num_fails = 1
    # getter for username    
    def get_uname(self):
        return self.username
    # setter for user last online time
    def set_time(self, time):
        self.last_online =  time
   # get last log in time 
    def get_time(self):
        return self.last_online
    # setter for login (true or false)    
    def set_login(self, login):
        self.login = login;
    # get log in status    
    def get_login(self):
        return self.login
   # get time of last log in time      
    def set_last_online(self, new_time):
        self.last_online = new_time
        

    # try to log in the client, return True if succeed
    def log_in(self, auth_users, any_users, block_duration):

        username = self.username
        password = self.password
        connectionSock = self.socket

        if (self.failed_log_in_3_times() == False and (self.get_time() + block_duration) < time.time()):
            print(">User was previously blocked, but time has passed block_duration")
            #print(get.time())
            #print(block_duration)
            self.reset_attmp()
            self.set_time(time.time())
        
        if (self.failed_log_in_3_times() == False):

            msg = 'Your account is blocked due to multiple login failures. Please try again later'
            connectionSock.send(msg.encode())
            return False  
                 
        message = ""
        # as long as the user < 3 can still log in, the log in the user
        if (self.failed_log_in_3_times() == True and self.get_login() == False):
            self.set_time(time.time())
            if username not in auth_users.keys():
                message = "You have entered unknown username"
                #print(message)               
                
            elif (auth_users[username] == password):
                self.success_log_in(username, connectionSock)
                return True
            else:
                
                self.fail_attmp()
                if self.failed_log_in_3_times() == True:
                    message = "Invalid Password. Please try again"
                else:
                    print("Blocked")
                    message = "Invalid Password. Your account has been blocked. Please try again later"
            print("send message to user" + message)
            connectionSock.send(message.encode())
        return False
        
    #authentication correct, log in success
    def success_log_in(self, username, connectionSock):
        print(">" + username + " has logged In")
        self.set_login(True)
        self.reset_attmp() 
        self.online.append(time.time())       
        message = "Welcome to the greatest messaging application ever!\n"
        connectionSock.send(message.encode())
    
    #reset attempt and set login as False    
    def log_out (self):
        print("logging out client here")
        self.reset_attmp()
        self.login = False            
