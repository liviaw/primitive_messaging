 # socket_echo_client.py
import socket
import sys
import threading
import datetime as dt
import time
import os
from threads_client import ThreadManager

#take in replies from the server and check if you have logged in
def log_in(sock, server_address):
  
    # Connect the socket to the port where the server is listening    
    username = ""
    password = ""
    
    try:
        username = input(">Username: ")
    except KeyboardInterrupt:
        os._exit(1)
        return
    
    try: 
        password = input(">Password: ")
    except KeyboardInterrupt:
        os._exit(1)
        return
        
    flag = False
    while (flag == False):                
        data = username + " " + password
        sock.send(data.encode())
        
        data = sock.recv(2048)
        print(">" + data.decode())           
        if data == b'Welcome to the greatest messaging application ever!\n':
            flag = True
            return True
        elif data == b'Invalid Password. Please try again':
            password = input(">Password: ")            
        elif data == b'Invalid Password. Your account has been blocked. Please try again later':
            sys.exit()
            #return False
        elif data == b'Your account is blocked due to multiple login failures. Please try again later':
            sys.exit()
            #return False
        elif data == b'Client already logged in':
            print(">Client exit")
            sys.exit()
        else:
            username = input(">Username: ")
            password = input(">Password: ")
           
    return False

# main function
if __name__ == '__main__':
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    
    connected_peers = {}
    
    # Create a TCP/IP socket
    #sock is the client socket        
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_address = (server_ip, server_port)
    print('>Python3 Client {} {}'.format(*server_address))
    sock.connect(server_address)  
    threadManager = ThreadManager(sock)  
    sock_list = [sock]
    if (log_in(sock, server_address) == True):    
        thread_rec = threading.Thread(target=threadManager.receive_thread, args=())
        thread_rec.daemon = True
        thread_rec.start()
        thread_send = threading.Thread(target=threadManager.send_thread)
        thread_send.daemon = True
        thread_send.start()
    
    #prevent main thread from closing the socket
    while True:
        time.sleep(1)
    #data =  "logout"
    #sock.send(data.encode())
       
    sock.close()

