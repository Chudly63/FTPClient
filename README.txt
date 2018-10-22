Alex M Brown
CS472
Assignment 2
README.txt

FTPClient.py

Usage: python FTPClient.py [-h] [-v] IP_ADDRESS LOG_FILE [PORT_NUMBER]
Parameters:
	-h			:	Display help message
	-v			:	Print log statements to stdout
	IP_ADDRESS	:	The IP address or host name of the FTP server
	LOG_FILE		:	The name of the file to write logs to
	PORT_NUMBER	:	The port number of the socket to connect to. Defualt = 21


Using the MAKEFILE

There is only one command in the makefile. Using this command allows you to run the client with any parameters you want, but the defaults will launch the client and connect you to the test server. 

Make run HOST={Your Host} LOG={Your Log File} PORT={Your Port}

Defaults:
	HOST = 10.246.251.93
	LOG = myLog.txt
	PORT = 21



IMPORTANT NOTES

	The PORT and EPRT commands don’t work on Tux, but they do run successfully on my Linux machine when connected to Dragonfly3. However, they only work in that environment when my firewall is disabled. Using them with my firewall enabled causes the client to time out and close. My sample run/log file show me using them on my laptop with the firewall disabled. 
