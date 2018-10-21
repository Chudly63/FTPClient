#!/usr/bin/env python
# CS472 - Homework #2
# Alex M Brown
# FTPClient.py
#
# This module contains all the functions for sending the commands for the FTP client

from socket import *
from socket import error as socket_error
import errno
import argparse
import sys
import re
import getpass
import datetime
import time


"""
Last Chance Checklist
[ ] Finish Documentation
[ ] Handle Filename Errors
[ ] Organize Commands into methods
[ ] DATA_SOCKET = None lines
"""



#GLOBAL VARIABLES
CONTROL_SOCKET = None                               #Socket for Control Connection
DATA_SOCKET = None                                  #Socket for Data Connection
TARGET_ADDR = None                                  #IP Address of the FTP server
TARGET_PORT = None                                  #Port Number for the Control Connection at the FTP server
LOG_FILE = None                                     #Name of the log file
BUFFER_SIZE = 4000                                  #Buffer for reading from FTP server
VERBOSE = False                                     #Should the client print logging info to stdout?
CRLF = "\r\n"                                       
SUPPORTED_COMMANDS = """\nSupported Commands:       
    about   cd      eprt    epsv
    get     help    ls      pasv
    port    put     pwd     quit\n"""
ACTIVE_MODE = False                                 #Is the server in active mode?


"""
Used for logging commands/replies/other important notes
Logs a written to a log file. If the -v flag was set, they are also written to stdout.
Input:
    msg: The message to be logged
"""
def log(msg):
    logfile = open(LOG_FILE,'a+')
    logfile.write(str(datetime.datetime.now())[:-3] + ": "+msg + "\n")
    logfile.close()
    if VERBOSE:
        print("#LOG: " + msg)


"""
Shut down the client with an error message
Input:
    msg: The message to be logged
"""
def terminate(msg):
    log("FATAL ERROR: " + msg)
    print("A fatal error has occured: " + msg)
    if CONTROL_SOCKET:
        CONTROL_SOCKET.close()
    if DATA_SOCKET:
        DATA_SOCKET.close()
    exit()
    

"""
Used for receiving information from the data connection. 
Input:
    socket: The socket to read everything from
Output:
    data: All of the data read from socket
"""
def recvall(socket):
    log("Reading info from the data connection...")
    blankCount = 0
    data = b""
    while(True):
        resp = socket.recv(BUFFER_SIZE)
        if len(resp) == 0:
            blankCount += 1
            time.sleep(.1)
        else:
            data += resp
            blankCount = 0
        if blankCount > 3:
            return data

"""
Establishes a connection between the client and the server
Input:
    str network : The network address of the server
    int port    : The port number of the server (default 21)
Output:
    On success, returns the socket for the control connection
    On fail, returns None
"""
def establish_connection(network, port = 21):
    CONNECTION = socket(AF_INET, SOCK_STREAM)
    log("Establishing connection at " + str((network, port)))
    try:
        CONNECTION.settimeout(5)
        CONNECTION.connect((network, port))
        return CONNECTION
    except socket_error as e:
        print("An unexpected error occured during connection establishment")
        print(e)
        return None



"""
Converts the FTP format (h1,h2,h3,h4,p1,p2) into a socket address
Input:
    str headers : A string in the format h1,h2,h3,h4,p1,p2
OutputL
    tuple : (IP_ADDR, PORT_NUM)
"""
def get_socket_address(headers):
    address_fields = headers.split(',')
    DEST_IP = '.'.join(address_fields[0:4])
    DEST_PORT = int(address_fields[4]) * 256 + int(address_fields[5])
    return (DEST_IP,DEST_PORT)



"""
Sends an FTP command over the control connection socket
Input:
    msg : a complete FTP command
Output:
    The reply from the server, or None if the message failed to send
"""
def send_command(msg):
    global CONTROL_SOCKET
    log("Sent: " + msg[:-2])
    try:    
        if CONTROL_SOCKET:                                                             #Replace with code for establishing connection
            CONTROL_SOCKET.send(msg)
            reply = CONTROL_SOCKET.recv(BUFFER_SIZE)
            log("Received: " + reply[:-2])
            return reply
        terminate("No Control Connection")
    except socket_error as e:
        print(e)
        terminate("Control connection lost.")


"""
Separates the response code and the response message from a server reply
Input:
    reply: An FTP server message
Output:
    tuple : (Response Code, Response Message)
"""
def parse_response(reply):
    if not reply:
        return None

    code = reply[0:3]
    text = reply[4:-2]
    return (code,text)


"""
Read a response from a socket.
Input:
    socket: The socket to read from
Output:
    response: The message read 
"""
def readSocket(socket):
    response = socket.recv(BUFFER_SIZE)
    log("Received: " + response[:-2])
    return response


"""
Send a file along a socket
Input:
    socket: The socket to transmit the data over
    filename: The name of the file to be sent
"""
def sendFile(socket, filename):
    sendFile = open(filename, "r+")
    sendBuffer = sendFile.read(BUFFER_SIZE)
    while not sendBuffer == "":
        print("Sending data...")
        socket.send(sendBuffer)
        sendBuffer = sendFile.read(BUFFER_SIZE)
    sendFile.close()
    socket.close()
    print("Done")


"""
Read the data for a file being send over the data connection
Input:
    socket: The socket for the data connection
    filename: The name of the file to save the data under
"""
def readFile(socket, filename):
    newFile = open(filename, "w+")
    newFile.write(recvall(socket))
    newFile.close()


#ACCESS CONTROL COMMANDS

"""
FTP USER COMMAND
Identifies the username of the current user.

Input: 
    username : Username of the user to be logged in
Output:
    tuple : (Response Code, Response Message)
"""
def ftp_user(username):
    msg = "USER " + username + CRLF
    
    reply = parse_response(send_command(msg))

    return reply


"""
FTP PASS COMMAND
Identifies the user's password.

Input:
    password : Password of the user to be logged in
Output:
    tuple : (Response Code, Response Message)
"""
def ftp_pass(password):
    msg = "PASS "+password+CRLF

    reply = parse_response(send_command(msg))
    
    return reply


"""
FTP CWD COMMAND
Allows the user to work with a different directory.

Input:
    pathname : The directory to change the server to
Output:
    tuple : (Respone Code, Response Message)
"""
def ftp_cwd(pathname):
    msg = "CWD "+pathname+CRLF

    reply = parse_response(send_command(msg))

    return reply 


"""
FTP QUIT COMMAND
Terminates user connection.

Output:
    tuple : (Response Code, Response Message)
"""
def ftp_quit():
    msg = "QUIT" + CRLF

    reply = parse_response(send_command(msg))
    
    return reply


#TRANSFER PARAMETER COMMANDS

"""
FTP PASV COMMAND
Requests the server to listen on a data port and wait for a connection.

Output:
    tuple : (Response Code, Response Message)
"""
def ftp_pasv():
    msg = "PASV" + CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP PORT COMMAND
Intructs the server to connect to the socket located at the host-port address

Input:
    headers : The address of the socket for the server to connect to. "h1,h2,h3,h4,p1,p2"
Output:
    tuple : (Response Code, Response Message) 
"""
def ftp_port(headers):
    
    msg = "PORT " + headers + CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP EPSV COMMAND
Requests the server to listen on a data port and wait for a connection

Output:
    tuple : (Response Code, Response Message)
"""
def ftp_epsv():
    msg = "EPSV 1" + CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP EPSV COMMAND
Allows for the specification of an extended address for the data connection

Input:
    protocol : The number indicating which internet protocol to use. 1 = IPv4, 2 = IPv6.
    address : The IP address of the socket address
    port : The port number of the socket address
Output:
    tuple : (Response Code, Response Message)
"""
def ftp_eprt(protocol, address, port):
    msg = "EPRT |"+str(protocol)+"|"+str(address)+"|"+str(port)+"|" + CRLF

    reply = parse_response(send_command(msg))

    return reply


#SERVICE COMMANDS


"""
FTP RETR COMMAND
Instructs the server to transfer a copy of the file PATHNAME to
the host at the other end of the data connection.

Input:
    pathname : The name of the file to be sent from the server
Output:
    tuple : (Response Code, Response Message)
"""
def ftp_retr(pathname):
    msg = "RETR "+pathname+CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP STOR COMMAND
Causes the server to accept the data transfered via the data connection 
and store the file at the server site. 

Input:
    pathname : The name of the file to be sent to the server
Output:
    tuple : (Response Code, Response Message)   
"""
def ftp_stor(pathname):
    msg = "STOR "+pathname+CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP PWD COMMAND
Causes the name of the current working directory to be returned in the reply.

Output:
    tuple : (Response Code, Response Message)
"""
def ftp_pwd():
    msg = "PWD" + CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP LIST COMMAND
Causes a list to be sent from the server to the passive DTP.

Input:
    pathname : Optional. Name of a directory or file to list information about
Output:
    tuple : (Response Code, Response Message)
"""
def ftp_list(pathname = None):
    if pathname:
        msg = "LIST " + pathname + CRLF
    else:
        msg = "LIST" + CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP SYST COMMAND
Used to find out the type of operating system at the server

Output:
    tuple : (Response Code, Response Message)
"""
def ftp_syst():
    msg = "SYST" + CRLF

    reply = parse_response(send_command(msg))

    return reply


"""
FTP HELP COMMAND
Gives the user information regarding the FTP client

Input:
    argument : Optional. Client argument that requires additional information
Output:
    Information about the client
"""
def ftp_help(argument = None):
    if argument == "":
        print(SUPPORTED_COMMANDS)
    elif argument == "about":
        print("about:       Show system information.")
    elif argument == "cd":
        print("cd:          Change current working directory.")
    elif argument == "eprt":
        print("eprt:        Extended Port. Tells the server what port to connect to for the data connection.")
    elif argument == "epsv":
        print("epsv:        Extended Passive. Tells the server to open a port so the client can establish a data connection.")
    elif argument == "get":
        peint("get:         Get file. Tells the server to send a file to the client. Requires data connection.")
    elif argument == "help":
        print("help:        Show information regarding supported commands.")
    elif argument == "ls":
        print("ls:          List. Show the information for all files in a directory. Requires data connection.")
    elif argument == "pasv":
        print("pasv:        Passive. Tells the server to open a port so the client can establish a data connection.")
    elif argument == "port":
        print("port:        Port. Tells the server what port to connect to for the data connection.")
    elif argument == "put":
        print("put:         Put file. Tells the server to store a file from the client. Requires data connection.")
    elif argument == "pwd":
        print("pwd:         Shows the current working direcoty.")
    elif argument == "quit":
        print("quit:        Terminate the connection to the server and close the client.")



"""
Logs the user into the FTP server.

Output:
    TRUE if the user is successfully logged in
    FALSE otherwise
"""
def ftp_login():
    user = raw_input('Enter Username: ')
    resp = ftp_user(user)
    if resp[0] == '230':
        return True
    if resp[0] == '331':
        pswd = getpass.getpass('Enter Password: ')
        resp = ftp_pass(pswd)
        if resp[0] == '230':
            return True
    
    print(resp[1])
    return False



# 
#   Read command line arguments. 
#

parser = argparse.ArgumentParser(description = "FTP client written by Alex M Brown.", epilog = "Have a nice day <3")
parser.add_argument('-v','--verbose', action='store_true', help="Print notes to cmdline. Useful for debugging")
parser.add_argument('IP_ADDR', nargs='?', default = '10.246.251.93', help="The IP Address or Name of the FTP server")
parser.add_argument('LOG_FILE', nargs='?', default = 'myLog.txt', help="The name of the file for the client logs")
parser.add_argument('PORT_NUM', nargs='?', default = 21, type = int, help="The port number of the FTP server. [Default = 21]")
args = vars(parser.parse_args(sys.argv[1:]))

TARGET_ADDR = args['IP_ADDR']
LOG_FILE = args['LOG_FILE']
TARGET_PORT = args['PORT_NUM']
VERBOSE = args['verbose']

try:
    TARGET_ADDR = gethostbyname(TARGET_ADDR)
except socket_error as e:
    print("An unexpected error occured while looking up host.")
    print(e)
    exit()

#
#   Esablish control connection and run the client
#


log("-----------------------------------New Session-----------------------------------")
CONTROL_SOCKET = establish_connection(TARGET_ADDR, TARGET_PORT)

if not CONTROL_SOCKET:
    print("Failed to establish control connection")
    exit()


readSocket(CONTROL_SOCKET)

#Log the user in
if not ftp_login():
    exit()

#Begin UI
print("Welcome to Alex Brown's FTP Client!")
print(SUPPORTED_COMMANDS)
while(True):
    choice = raw_input("myFTP> ")

    #DO HELP
    if choice == 'help':
        help_command = raw_input("Select command: ")
        ftp_help(help_command)

    #DO PASSIVE
    elif choice == 'pasv':
        print("Entering passive mode...")
        resp = ftp_pasv()
        if resp[0] == '227':
            #Search the response string for the socket headers: (h1,h2,h3,h4,p1,p2).
            address = re.search('\(.*\)', resp[1])
            address = address.group(0)[1:-1]
            #Parse the socket address and establish the data connection.
            socket_address = get_socket_address(address)
            DATA_SOCKET = establish_connection(socket_address[0], socket_address[1])
            if DATA_SOCKET:
                ACTIVE_MODE = False
                print("Data connection ready.")
            else:
                print("Error establishing data connection")
        else:
            print(resp[0])
            
    #DO PORT
    elif choice == 'port':
        print("Entering active mode...")
        #Get the IP Address of the machine and open a port on it
        my_ip = CONTROL_SOCKET.getsockname()[0]

        DATA_SOCKET = socket(AF_INET, SOCK_STREAM)
        DATA_SOCKET.bind((my_ip, 0))

        #Generate the headers for the PORT command (h1,h2,h3,h4,p1,p2)
        my_port = int(DATA_SOCKET.getsockname()[1])
        p2 = my_port % 256
        p1 = (my_port - p2) / 256

        h = ','.join(my_ip.split('.'))
        headers = h + ',' + str(p1) + ',' + str(p2)

        #Begin listening on the newly opened port and send the PORT command
        DATA_SOCKET.listen(1)
        resp = ftp_port(headers)

        if resp[0] == '200':
            ACTIVE_MODE = True
            print("Data connection port ready.")
        else:
            DATA_SOCKET.close()
            print(resp[1])

    #DO EXTENDED PASSIVE
    elif choice == 'epsv':
        print("Entering passive mode...")
        resp = ftp_epsv()
        if resp[0] == '229':

            #Search the response string for the port number
            port = re.search('\|\|\|.*\|', resp[1])
            port = port.group(0)[1:-1].strip('|')

            #Establish the data connection
            DATA_SOCKET = establish_connection(TARGET_ADDR, int(port))
            if DATA_SOCKET:
                ACTIVE_MODE = False
                print("Data connection ready.")
            else:
                print("Error establishing data connection")

    #DO EXTENDED PORT
    elif choice == 'eprt':
        my_ip = CONTROL_SOCKET.getsockname()[0]

        DATA_SOCKET = socket(AF_INET, SOCK_STREAM)
        DATA_SOCKET.bind((my_ip, 0))

        my_port = DATA_SOCKET.getsockname()[1]

        DATA_SOCKET.listen(1)
        resp = ftp_eprt(1, my_ip, my_port)
        if resp[0] == '200':
            ACTIVE_MODE = True
            print("Data connection port ready.")
        else:
            DATA_SOCKET.close()
            print(resp[1])

    #DO PWD
    elif choice == 'pwd':
        resp = ftp_pwd()
        print(resp[1])

    #DO LIST
    elif choice == 'ls':
        if not DATA_SOCKET:
            print("Need to establish data connection. Use pasv, port, eprt, or epsv first")
        else:
            subject = raw_input("Enter optional file/directory: ")
            resp = ftp_list(subject)
            if resp[0] == '150':
                if ACTIVE_MODE:
                    DATA_SOCKET, address = DATA_SOCKET.accept()
                    log("Accepted data connection from Server")
                list_info = recvall(DATA_SOCKET)
                print(list_info)
                resp = parse_response(readSocket(CONTROL_SOCKET))
                if not resp[0] == '226':
                    print(resp[1])
                    DATA_SOCKET.close()
            else:
                print(resp[1])

    #DO CWD
    elif choice == 'cd':
        directory = raw_input("Enter directory name: ")
        resp = ftp_cwd(directory)
        print(resp[1])

    #DO RETRIEVE
    elif choice == 'get':
        if not DATA_SOCKET:
            print("Need to establish data connection. Use pasv, port, eprt, or epsv first")
        else:
            filename = raw_input("Enter name of desired file: ")
            resp = ftp_retr(filename)
            if resp[0] == '150' or resp[0] == '125':
                savename = raw_input("Save file as: ")
                if ACTIVE_MODE:
                    DATA_SOCKET, address = DATA_SOCKET.accept()
                    log("Accepted data connection from Server")
                readFile(DATA_SOCKET, savename)
                resp2 = parse_response(readSocket(CONTROL_SOCKET))
                if not resp2[0] == '226':
                    print(resp2[1])
                    DATA_SOCKET.close()
            else:
                print(resp[1])

    #DO STORE
    elif choice == 'put':
        if not DATA_SOCKET:
            print("Need to establish data connection. Use pasv, port, eprt, or epsv first")
        else:
            filename = raw_input("Enter name of your file: ")
            resp = ftp_stor(filename)
            if resp[0] == '150' or resp[0] == '125':
                if ACTIVE_MODE:
                    DATA_SOCKET, address = DATA_SOCKET.accept()
                    log("Accepted data connection from Server")
                sendFile(DATA_SOCKET, filename)
                resp = parse_response(readSocket(CONTROL_SOCKET))
                if not resp[0] == '226':
                    print(resp[1])
                    DATA_SOCKET.close()
            else:
                print(resp[1])

    #DO SYSTEM
    elif choice == 'about':
        resp = ftp_syst()
        print(resp[1])

    #DO QUIT
    elif choice == 'quit':
        ftp_quit()
        exit()

    #INVALID COMMAND
    else:
        print(SUPPORTED_COMMANDS)
