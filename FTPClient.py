#
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

#GLOBAL VARIABLES
CONTROL_SOCKET = None
DATA_SOCKET = None
TARGET_ADDR = None
TARGET_PORT = None
LOG_FILE = None

verbose = True
CRLF = "\r\n"




def log(msg):
    if verbose:
        print(msg)

"""
Establishes the control connection between the client and the server
Input:
    str network : The network address of the server
    int port    : The port number of the server (default 21)
Output:
    On success, returns the socket for the control connection
    On fail, returns None
"""
def establish_control_connection(network, port = 21):
    CONTROL = socket(AF_INET, SOCK_STREAM)
    try:
        CONTROL.settimeout(5)
        CONTROL.connect((network, port))
        CONTROL.settimeout(0)
        reply = CONTROL.recv(1024)
        log(reply)
        return CONTROL
    except socket_error as e:
        print("An unexpected error occured during connection establishment")
        print(e)
        return None


"""
Sends an FTP command over the control connection socket
Input:
    str msg : a complete FTP command
Output:
    The reply from the server, or None if the message failed to send
"""
def send_command(msg):
    global CONTROL_SOCKET
    try:
        if CONTROL_SOCKET:                                                             #Replace with code for establishing connection
            CONTROL_SOCKET.send(msg)
            reply = CONTROL_SOCKET.recv(1024)
            log(reply)
            return reply
        return None
    except socket_error as e:
        print(e)
        return None

#ACCESS CONTROL COMMANDS

"""
FTP USER COMMAND
Identifies the username of the current user.
First command run after establishing control connection.
Format: USER<sp><username><CRLF>
Replies: 200, 530, 500, 501, 421, 331, 332

Input: 
    str username : Username of the user to be logged in
Output:

"""
def ftp_user(username):
    msg = "USER " + username + CRLF
    log(msg)
    
    reply = send_command(msg)

    return reply


"""
FTP PASS COMMAND
Identifies the user's password.
Must be immediatley preceded by the USER command.
Format: PASS<sp><password><CRLF>
Replies: 230, 202, 530, 500, 501, 503, 421, 332

Input:
    str password : Password of the user to be logged in
Output:

"""
def ftp_pass(password):
    msg = "PASS "+password+CRLF
    log(msg)

    reply = send_command(msg)
    
    return reply


"""
FTP CWD COMMAND
Allows the user to work with a different directory.
Format: CWD<sp><pathname><CRLF>
Replies: 250, 500, 501, 502, 421, 530, 550

Input:
    str pathname : The directory to change the server to
Output:

"""
def ftp_cwd(pathname):
    msg = "CWD "+pathname+CRLF
    log(msg)

    reply = send_command(msg)

    return reply 


"""
FTP QUIT COMMAND
Terminates user connection.
Format: QUIT<CRLF>
Replies: 221, 500
"""
def ftp_quit():
    msg = "QUIT" + CRLF
    log(msg)

    reply = send_command(msg)
    
    return reply


#TRANSFER PARAMETER COMMANDS

"""
FTP PASV COMMAND
Requests the server to listen on a data port and wait for a connection.
Format: PASV<CRLF>
Replies: 227, 500, 501, 421, 530
"""
def ftp_pasv():
    msg = "PASV" + CRLF
    log(msg)

    reply = send_command(msg)

    return reply


"""
FTP PORT COMMAND
Intructs the server to connect to the socket located at the host-port address
Format: POST<sp><host-port><CRLF>
    Where: <host-port> := <h1><h2><h3><h4><p1><p2>
Replies: 200, 500, 501, 421, 530
"""
def ftp_port(address):
    return 1


"""
FTP EPSV COMMAND
Requests the server to listen on a data port and wait for a connection
Format: EPSV<sp><network protocol>
Replies: TBD
"""
def ftp_epsv():
    return 1


"""
FTP EPSV COMMAND
Allows for the specification of an extended address for the data connection
Format: EPRT<sp><d><network protocol><d><network address><d><TCP Port><d>
    Where: <d> := | or any other delimiter character
           <network protocol> Indicates the protocol to be used. 1 = IPv4, 2 = IPv6
           <network address> Protocol specific representation of a network address. (i.e. 132.235.1.2)
           <TCP Port> String representation of the port number on which the host is listening
    Example: EPRT |1|132.253.1.2|6275|
Replies: TBD
"""
def ftp_eprt():
    return 1


#SERVICE COMMANDS


"""
FTP RETR COMMAND
Instructs the server to transfer a copy of the file PATHNAME to
the host at the other end of the data connection.
Format: RETR<sp><pathname><CRLF>
Replies: 125, 150, 110, 226, 250, 425, 426, 451, 450, 550, 500, 501, 421, 530
"""
def ftp_retr(pathname):
    msg = "RETR "+pathname+CRLF
    log(msg)

    reply = send_command(msg)

    return reply


"""
FTP STOR COMMAND
Causes the server to accept the data transfered via the data connection 
and store the file at the server site. 
Format: STOR<sp><pathname><CRLF>
Replies: 125, 150, 110, 226, 250, 425, 426, 451, 551, 552, 532, 450, 452, 553, 500, 501, 421, 530
"""
def ftp_stor(pathname):
    msg = "STOR "+pathname+CRLF
    log(msg)

    reply = send_command(msg)

    return reply


"""
Causes the name of the current working directory to be returned in the reply.
Format: PWD<CRLF>
Replies: 257, 500, 501, 502, 421, 550
"""
def ftp_pwd():
    msg = "PWD" + CRLF
    log(msg)

    reply = send_command(msg)

    return reply


"""
Causes a list to be sent from the server to the passive DTP.
If the pathname argument specifies a directory or other group of files,
the server should transfer a list of files in the specified directory.
If the pathname specifies a file, then the server will send curent info
on the file.
A null argument implies the user's current working or default directory.
Format: LIST[<sp><pathname>]<CRLF>
Replies: 125, 150, 226, 250, 425, 426, 451, 450, 500, 501, 502, 421, 530
"""
def ftp_list(pathname = None):
    if pathname:
        msg = "LIST " + pathname + CRLF
    else:
        msg = "LIST" + CRLF
    log(msg)

    reply = send_command(msg)

    return reply


"""
FTP SYST COMMAND
Used to find out the type of operating system at the server
Format: SYST<CRLF>
Replies: 215, 500, 501, 502, 421
"""
def ftp_syst():
    msg = "SYST" + CRLF
    log(msg)

    reply = send_command(msg)

    return reply


"""
FTP HELP COMMAND
Causes the server to send helpful information regarding its implementation
status over the control connection.
The command may take any command name as an argument and return more specific
information as a response.
Format: HELP[<sp><string>]<CRLF>
Replies: 221, 214, 500, 501, 502, 421
"""
def ftp_help(argument = None):
    if argument:
        msg = "HELP " + argument + CRLF
    else:
        msg = "HELP" + CRLF
    log(msg)

    reply = send_command(msg)

    return reply


# 
#   Read command line arguments. 
#

parser = argparse.ArgumentParser(description = "FTP client written by Alex M Brown.", epilog = "Have a nice day <3")
parser.add_argument('IP_ADDR', help="The IP Address or Name of the FTP server")
parser.add_argument('LOG_FILE', help="The name of the file for the client logs")
parser.add_argument('PORT_NUM', nargs='?', default = 21, type = int, help="The port number of the FTP server. [Default = 21]")
args = vars(parser.parse_args(sys.argv[1:]))

TARGET_ADDR = args['IP_ADDR']
LOG_FILE = args['LOG_FILE']
TARGET_PORT = args['PORT_NUM']


CONTROL_SOCKET = establish_control_connection("10.246.251.93", 21)
#CONTROL_SOCKET = establish_control_connection(TARGET_ADDR, TARGET_PORT)
if not CONTROL_SOCKET:
    exit()
ftp_user("cs472")
ftp_pass("hw2ftp")
