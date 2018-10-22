HOST = 10.246.251.93
LOG = myLog.txt
PORT = 21

run : 
	python FTPClient.py ${HOST} ${LOG} ${PORT}
