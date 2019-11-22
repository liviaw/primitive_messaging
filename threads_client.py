 # socket_echo_client.py
import socket
import sys
import threading
import datetime as dt
import time
import os
import select

connect_sockets = {}
socket_to_server = None



"""
socket_to_server => Socket for the connection to the server
p2p_server => Server object for p2p connections
peer_list => List of p2p clients connected to OUR p2p server

"""

# a class structure that holds information regarding the client thread
class ThreadManager():
    def __init__(self, server_socket):
        self.socket_to_server = server_socket
        self.p2p_server = None
        self.peers = {}
        self.peers_reverse_map = {}
        self.awaiting_connections = []

    # thread to listen and handle sending 
    def send_thread(self):
        while True:
            try:
                data = input("")
            except KeyboardInterrupt:
                sock.close()
                sys.exit(1)
                return 
            if (data == ""):
                continue   

            if (data.startswith("private ")):
                
                if (len(data.split()) < 2):
                    print(">Please enter [startprivate] [message]... [message]")
                    continue
                result = data.split(" ", 2)
                receiver_name = result[1]
                if (receiver_name not in self.peers):
                    print("Error. Private messaging to " + receiver_name + " not enabled")
                else:
                    sock = self.peers[receiver_name]
                    print("DELETE this print later " + data)
                    message = "(private): " + result[2]
                    sock.send(message.encode())
                    time.sleep(0.05)
                continue
            elif (data.startswith("stopprivate ")):
                result = data.split()
                if (len(result) > 2):
                    sock.send(">Error. Please enter only 1 user to stop private message")
                elif (len(resul) == 1):
                    sock.send(">Error. Please enter [stopprivate] [username]")   
                elif (len(result) == 2):
                    if (result[1] not in self.peers):
                        sock.send("Error. There does not exist an active private messaging session with " + result[1])
                    else:
                        receiver_name = str(self.result[1])
                        print("Stop private messaging with " + result[1])
                        del self.peers_reverse_map[self.user[receiver_name]]
                        del self.user[receiver_name]
                        message = "stopprivate " + str(p2p_server)
                        sock.send(message.encode())
            # handling and starting private connections            
            else:
                if data.startswith("startprivate "):
                    if (len(data.split()) != 2):
                        print(">Please enter [startprivate] [username]")
                        continue
                    elif (data.split()[1] in self.peers):
                        print(">Private connection to " + data.split()[1] + " is still here")
                        continue
                    # appending receiver name
                    self.awaiting_connections.append(data.split(" ")[1])
                    
                #send command to Server
                print(">Sent to server: " + data)
                self.socket_to_server.send(data.encode())
                time.sleep(0.05)
                continue
                    
        self.socket_to_server.close()
        return

    #thread for receiving messages from server and p2p
    def receive_thread(self): 
        while True:
            readList = [self.socket_to_server] + list(self.peers.values())
            #print(readList)
            if self.p2p_server is not None:
                readList.append(self.p2p_server)
            try:
                readable, write, execute = select.select(readList, [], [], 1)
            except(ConnectionResetError, OSError, SystemError, ValueError, TypeError):
                print(">Oh no! Something is not right. Stopping program.")
                return
            
            
            for sock in readable:
                time.sleep(1)
                if (sock == self.socket_to_server):
                    try:
                        data = sock.recv(2048).decode()
                        if (data == ""):
                            continue
                        print(data)
                    except ConnectionResetError:
                        print('caught error')
                        return
                    except KeyboardInterrupt:
                        sock.close()
                        sys.exit(1)
                        return
                    result = data.split()                    
                    if (data == "logout" ):
                        sock.close()
                        os._exit(1)
                    #send to receiver
                    elif (data == "start p2p"):
                        print(">Receiver receiving P2P request")
                        self.start_p2p()
                    #send to receiver, who will establish the connection
                    elif (data.startswith("connect p2p initiator")):
                        self.connect_to_initiator_p2p(data.split())
                    elif (result[0] == "(private):" ):
                        temp = str(sock)
                        sender_name = self.peers_reverse_map[temp]
                        #send to server
                        print("> " + sender_name + result)
                    elif (data.startswith("stopprivate")):
                        result = data.split()
                        sender_sock = str(self.result[1])
                        print(result[1] + ": Stop private messaging with " + result[1])
                        del self.peers_reverse_map[sender_sock]
                        del self.user[self.peers_reverse_map[sender_sock]]
                            
                    
                    continue
                # whe you are receiveing as a p2p server
                elif sock is self.p2p_server:
                    if len(self.awaiting_connections) == 0:
                        continue                        
                    newp2pconnection, addr = sock.accept()
                    # i am the receiver here
                    receiver_name = self.awaiting_connections.pop(0)
                    
                    self.peers[receiver_name] = newp2pconnection
                    self.peers[str(newp2pconnection)] = receiver_name
                else:
                   
                    #handles private receiving
                    # p2p dont use recv
                    
                    if (sock is self.p2p_server):
                        print(">Error. Cannot peer-connect to self")
                        return
                    # no validity checker is required
                    newp2pconnection, addr = sock.accept()

         
        sock.close()
        os._exit(1)
        return

    
    #Server send initiator data to receiver        
    def connect_to_initiator_p2p(self, result):
        time.sleep(1)
        #initiator's name
        sender_name = result[3]
        #sock is the client socket        
        receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        receiver_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #host = 'localhost'
        #port_str = result[4]
        
        host, port = result[4].split("|")
        port = int(port)
        initiator_addr = (host, port)

        try:
            receiver_sock.connect(initiator_addr)
        except ConnectionRefusedError:
            print(">P2P connection failed from " + sender_name )
        #sys.exit()
        # a list of connected socket
        #receivers side
        self.peers[sender_name] = receiver_sock
        temp = str(receiver_sock)
        self.peers_reverse_map[temp] = sender_name
        '''
        try:
            receiver_sock.send(sender_name.encode())
        except BrokenPipeError:
            print(">BrokenPipeError. Fail to connect from " + sender_name)
        '''
        message = "succeed"
        self.socket_to_server.send(message.encode())
        print(">Start private messaging")    
        #p2p is now set up
        return sender_name

    # initiator start listening    
    def start_p2p(self):
        if self.p2p_server is not None:
            return
        print(">Establishing P2P connection")
        
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = self.socket_to_server.getsockname()[1]
        #my_peer_address = ('localhost', port)
        my_peer_address = ('0.0.0.0', port)
         
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the port
        server.bind(my_peer_address)
        
        # Listen for incoming connections
        server.listen(1)
        self.p2p_server = server
        #self.socket_to_server.send(str(server.getsockname()[1]).encode())

# tuple to string converter
def tupleToDelimString(tup):
    return "|".join([str(item) for item in tup])
