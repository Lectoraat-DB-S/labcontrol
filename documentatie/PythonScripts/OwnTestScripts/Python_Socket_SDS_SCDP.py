#!/usr/bin/env python
#-*- coding:utf-8 –*-
#-----------------------------------------------------------------------------
# The short script is a example that open a socket, sends a query to return a
#screen dump from the scope, saves the screen dump as a BMP in the python folder,
#and closes the socket.
#
#Currently tested on SDS1000X-E,2000X-E, and 5000X models
#
#No warranties expressed or implied
#
#SIGLENT/JAC 03.2019
#
#-----------------------------------------------------------------------------
import socket # for sockets
import sys # for exit
import time # for sleep
#-----------------------------------------------------------------------------

remote_ip = "192.168.55.100" # should match the instrument’s IP address
port = 5025 # the port number of the instrument service

def SocketConnect():
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print ('Failed to create socket.')
        sys.exit();
    try:
        #Connect to remote server
        s.connect((remote_ip , port))
        s.setblocking(0) # non-blocking mode, an exception occurs when no data is detected by the receiver
        #s.settimeout(3) 
    except socket.error:
        print ('failed to connect to ip ' + remote_ip)
    return s

def SocketQuery(Sock, cmd):
    try :
        #Send cmd string
        Sock.sendall(cmd)
        Sock.sendall(b'\n') #Command termination
        time.sleep(1)
    except socket.error:
        #Send failed
        print ('Send failed')
        sys.exit()

    data_body = bytes() 
    while True:
        try:
            time.sleep(0.01)
            server_replay = Sock.recv(8000)
            #print(len(server_replay))
            data_body += server_replay
        except BlockingIOError:
            print("data received complete..")
            break
    return data_body
    '''
    PACK_LEN = 768067#the packet length you will receive;
    #SDS5000X is 2457659;SDS1000X-E/2000X-E is 768067
    had_received = 0    
    data_body = bytes() 
    while had_received < PACK_LEN:
        part_body= Sock.recv(PACK_LEN - had_received)
        data_body +=  part_body
        part_body_length = len(part_body)
        #print('part_body_length', part_body_length)
        had_received += part_body_length
    return data_body
    '''


def SocketClose(Sock):
    #close the socket
    Sock.close()
    time.sleep(5)

def main():
    global remote_ip
    global port
    global count

    #Open a file
    file_name = "SCDP.bmp"

    # Body: Open a socket, query the screen dump, save and close
    s = SocketConnect()
    qStr = SocketQuery(s, b'SCDP') #Request screen image
    print(len(qStr))
    f=open(file_name,'wb')
    f.write(qStr)
    f.flush()
    f.close()

    SocketClose(s)
    sys.exit

if __name__ == '__main__':
    proc = main()
