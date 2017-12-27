# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 11:23:00 2017

@author: dangr
"""
import socket
import threading
import time
import subprocess
import multiprocessing
import re
import os
import pickle
from collections import OrderedDict
import datetime

#FUNCTION THAT PINGS A SINGLE IP ADDRSESS
def ping(ip):
    #CREATE PROCESS THAT PINGS IP ADDRESSES
    subprocess.Popen(['ping', '-n', '1', '-w', '500', ip], stdout=subprocess.PIPE).communicate()[0]

#FUNCTION THAT PINGS ALL IP ADDRESSES 
def pingSweep():
    #CREATE RANGE OF IP ADDRESSES
    ips = ('192.168.1' + '.%d' % i for i in range(1, 255))   
    
    #PREVENTS MULTIPROCESSING FROM FREEZING
    if __name__ == '__main__':
        multiprocessing.freeze_support()
        with multiprocessing.Pool(100) as pool:
            pool.map(ping, ips) 
    
    #GATHER OUTPUT FROM SUBPROCESS        
    output = subprocess.check_output(['arp', '-a']).decode('utf-8')
        
    #GATHER ALL AVAILABLE IP ADDRESSES FOUND
    for ip in re.findall('(192\.168\.1\.\d*)', output):
        if ip != my_ip:
            active_ips.append(ip)

#RETURNS FILES IN SERVER'S FILES FOLDER
def getFiles():
    hash_table = {}
    for filename in os.listdir():
        hash_table[filename] = getFileTime(filename)
        #IGNORE FILES THAT ARE DELETED
        if hash_table[filename] != None:
            hash_table[filename]   
    return OrderedDict(hash_table)
        

#RETURNS FILE LAST MODIFICATION TIME
def getFileTime(filename):
    try:
        time = datetime.datetime.fromtimestamp(os.path.getmtime(getFilePath(filename)))
    #IF FILE DOES NOT EXIST
    except:
        return None
    return time
    
#RETURNS FILE PATH
def getFilePath(filename):
    return os.path.join(os.getcwd(), filename)

#RETURNS FILE SIZE    
def getFileSize(filename):
    return os.path.getsize(getFilePath(filename))
          
#LISTENING SOCKET
class Listen:
    connections = []
    peers = []  
    
    #INITIALIZES THE SERVER
    def __init__(self):        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)            
        try:
            sock.bind(('0.0.0.0', 7777))
            sock.listen(1)  
            time.sleep(1)
            print("Listening for connections...")
            
            while True:
                c, a = sock.accept()         
                
                #THREAD FOR HANDLING SERVER LOGIC
                logic = threading.Thread(target=self.handler, args=(c, a))
                logic.daemon = True
                logic.start()
                
                self.connections.append(c)
                print(str(a[0]) + ":" +str(a[1]) + " is connected.")
                    
        except:
            print("ERROR: Socket binding")
            
    
    def handler(self, c, a):
        print("Logic thread running...")
        while True:
            #INITIALIZE HASH TABLE FOR FILE DIFFERENCE
            hash_difference = {}
            hash_table = getFiles()
            
            #PRINT OUT MY HASH TABLE
            print("\nHERE ARE YOUR FILES")
            for filename in hash_table.keys():
                print("   " + filename + " : " + str(getFileTime(filename)))
                            
            #SEND FILE HASH TABLE TO CLIENT
            c.send(pickle.dumps(hash_table))
            
            #RECEIVE HASH TABLE FOR FILE DIFFERENCE 
            hash_difference = OrderedDict(pickle.loads(c.recv(512)))
            
            #IF THERE IS A DIFFERENCE, PERFORM FILE TRANSFIER
            if any(hash_difference) == True:
            
                #DISPLAY HASH DIFFERENCE
                print("\nLIST OF FILES TO SEND: ")
                for filename in hash_difference.keys():     
                    print("\t" + filename)
                    hash_difference[filename] = getFileSize(filename)
                    
                #SEND HASH WITH SIZE
                c.sendall(pickle.dumps(hash_difference))
                
                input("")
                
                #FILE TRANSFER SERVER --> CLIENT
                for filename in hash_difference.keys():
                    print("\nSENDING: " + filename)
                    with open(filename, 'rb') as send_file:
                        while hash_difference[filename] > 0:
                            bytes_to_send = send_file.read(512)
                            c.sendall(bytes_to_send)
                            hash_difference[filename] -= 512
                            while True:
                                signal = c.recv(512)
                                if signal.decode() == "DONE":
                                    break
                    send_file.close()
                    print("FILE HAS BEEN SENT: " + filename)                
                print("\nALL FILES HAVE BEEN SENT.") 
                
            else:
                print("\nThere are no files to be sent.")
                
            #RECEIVE HASH DIFFERENCE 
            hash_difference = OrderedDict(pickle.loads(c.recv(512)))
            
            #IF THERE IS A DIFFERENCE, PERFORM FILE TRANSFER
            if any(hash_difference) == True:
                #DISPLAY HASH DIFFERENCE
                print("\nLIST OF FILE(S) TO BE RECEIVED: ")
                for filename in hash_difference.keys():     
                    print("\t" + filename)
                    
                input("")
                
                #FILE TRANSFER CLIENT --> SERVER
                for filename in hash_difference.keys():
                    print("\nRECEIVING: " + filename)                
                    with open(filename, 'wb+') as write_file:
                        bytes_to_write = b''
                        while hash_difference[filename] > 0:
                            bytes_to_write += c.recv(512)
                            hash_difference[filename] -= 512
                            c.sendall("DONE".encode()) 
                        write_file.write(bytes_to_write)
                    write_file.close()                            
                    print("FILE HAS BEEN RECEIVED: " + filename)               
                print("\nFILE TRANSFER IS COMPLETE.")      

            #NO DIFFERENCE, THEN FILE TRANSFER IS SKIPPED     
            else:
                print("\nThere are no files to be received.")
            
            print("\nYour files are up-to-date.")
            
            #PRINT OUT FILES
            print("\nHERE ARE YOUR UPDATED FILES")
            hash_table = getFiles()
            for filename in hash_table.keys():
                print("   " + filename + " : " + str(hash_table[filename]))
            
            #SLEEP BEFORE THE NEXT SCAN
            time.sleep(20)

#CLIENT CLASS
class Connecting:           
    #INITIALIZES THE CLIENT
    def __init__(self):
        while True:
            #CONNECTS TO ACTIVE IP ADDRESSES THAT ARE NOT ALREADY PEERS
            for address in active_ips:
                if address not in peerList:
                    #CREATE SOCKET
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    try:
                        #BIND SOCKET
                        sock.connect((address, 7777))
                        print("Connected to: "+address)
                        
                        #RUN THREAD THAT HANDLES LOGIC
                        logic = threading.Thread(target=self.handler, args=(sock, address))
                        logic.daemon = True
                        logic.start()
                        
                        #ADD TO PEER LIST
                        peerList.append(address)
                    except:
                        pass
            time.sleep(3)
    
    #LOGIC THREAD FOR CONNECTING SOCKET        
    def handler(self, c, address):
        print("Logic thread running...")
        while True:
            #INITIALIZE HASH TABLE FOR FILE DIFFERENCES
            hash_difference = {}
            hash_table = OrderedDict(getFiles())
            
            #PRINT OUT MY HASH TABLE
            print("\nHERE ARE YOUR FILES")
            for filename in hash_table:
                print("   " + filename + " : " + str(getFileTime(filename)))
            
            #RECEIVE HASH TABLE FROM SERVER
            receive_hash = pickle.loads(c.recv(512))
            
            #CALCULATE HASH DIFFERENCES
            receive_files = OrderedDict(dict(receive_hash.items() - hash_table.items()))
            send_files = OrderedDict(dict(hash_table.items() - receive_hash.items()))
            
            #CALCULATE & SEND HASH DIFFERENCE
            hash_difference = receive_files
            c.send(pickle.dumps(hash_difference))   
            
            #IF THERE IS A FILE DIFFERENCE, PERFORM FILE TRANSFER SERVER --> CLIENT
            if any(hash_difference) == True:
            
                #RECEIVE FILES FROM SERVER
                print("\nLIST OF FILE(S) TO BE RECEIVED: ")
                for filename in hash_difference.keys():
                    print("\t" + filename)
                
                #RECEIVE HASH WITH SIZE
                hash_difference = pickle.loads(c.recv(512))
                
                input("")
                
                #FILE TRANSFER SERVER --> CLIENT
                for filename in hash_difference.keys():
                    print("\nRECEIVING: " + filename)                
                    with open(filename, 'wb+') as write_file:
                        bytes_to_write = b''
                        while hash_difference[filename] > 0:
                            bytes_to_write += c.recv(512)
                            hash_difference[filename] -= 512
                            c.sendall("DONE".encode())  
                        write_file.write(bytes_to_write)
                    write_file.close()                            
                    print("FILE HAS BEEN RECEIVED: " + filename)               
                print("\nFILE TRANSFER IS COMPLETE.")
            
            #NO FILE DIFFERENCE, SKIP FILE TRANSFER SERVER --> CLIENT
            else:
                print("\nThere are no files to be received.")
                
            #CALCULATE & SEND HASH DIFFERENCE WITH SIZE
            hash_difference = send_files
            for filename in hash_difference:
                hash_difference[filename] = getFileSize(filename)
            hash_difference = OrderedDict(hash_difference)
            c.sendall(pickle.dumps(hash_difference))
                
            #IF THERE IS A FILE DIFFERENCE, PERFORM FILE TRANSFER CLIENT --> SERVER
            if any(hash_difference) == True:  
                #RECEIVE FILES FROM SERVER
                print("\nHERE ARE THE FILES TO BE SENT: ")
                for filename in hash_difference.keys():
                    print("\t" + filename) 
                    
                input("")
                
                #FILE TRANSFER CLIENT --> SERVER
                for filename in hash_difference.keys():
                    print("\nSENDING: " + filename)
                    with open(filename, 'rb') as send_file:
                        while hash_difference[filename] > 0:
                            bytes_to_send = send_file.read(512)
                            c.sendall(bytes_to_send)
                            hash_difference[filename] -= 512
                            while True:
                                signal = c.recv(512)
                                if signal.decode() == "DONE":
                                    break
                    send_file.close()                
                    print("FILE HAS BEEN SENT: " + filename)                
                print("\nFILE TRANSFER COMPLETE.")
                          
            #NO DIFFERENCE, SKIP FILE TRANSFER CLIENT --> SERVER
            else:
                print("\nThere are no files to be sent.")
                
            print("\nYour files are up-to-date.")

            #UPDATE HASH TABLE
            hash_table = OrderedDict(getFiles())
            print("\nHERE ARE YOUR UPDATED FILES")
            for filename in hash_table.keys():
                print("   " + filename + " : " + str(hash_table[filename]))
            
            #SLEEP BEFORE THE NEXT SCAN
            time.sleep(20)

#MAIN CLASS    
if __name__ == '__main__':  
    #GATHER NETWORK DATA
    active_ips = []
    peerList = []
    hash_table = {}
    folder = os.path.join(os.getcwd(), 'files\\')
    os.chdir(folder)
    
    print("This is dir: " + folder)  
    my_ip = '192.168.1.3'    
    print("This is my IP: " + my_ip + "\n")

    #PING SWEEP
    print("Performing ping sweep...")
    pingSweep()
    print("List of online IP addresses: ")
    for ip in active_ips:
        print("  " + ip)
    print()
         
    ######################################
    
    #CREATES SOCKET TO LISTEN FOR CONNECTIONS
    listen = threading.Thread(target=Listen)
    print("Listen thread initiated.")
    listen.start()
    
    #CREATES SOCKET TO CONNECT TO OTHER CONNECTIONS
    connect = threading.Thread(target=Connecting)
    print("Connect thread initiated.")
    connect.start()
    