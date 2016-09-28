#!/usr/bin/python
# -*- coding: UTF-8 -*-

import Queue
import threading
import os
import urllib2

threads = 10

# 주제 : 웹 어플리케이션을 매핑하기 (Mapping Open Source Web App Installations)
# [*] 일종의 웹 스파이더 같은 프로그램이라고 보면될 것 같다. 
# 1) We begin by defining the remote target website and the local directory into 
# which we have downloaded and extracted the web application. 
# We also create a simple list of file extensions that we are not insterested in 
# fingerprinting. This list can be different depending on the target application. 
target = "www.jw.com"
directory = "/var/www"  # 앱 파일을 다운로드 받은 경로 
filters = [".jpg",".gif",".png",".css"] # 관심없는 파일 확장자 리스트

os.chdir(directory)

# 2) The web_paths variable is our Queue object where we will store the files 
# that we'll attempt to locate on the remote server. 
# 파일을 저장할 큐 오브젝트
web_paths = Queue.Queue()

# 로컬 디렉토리의 웹 어플리케이션을 순회하기 위해 os.walk 펑션을 사용. 
for root,dirs,files in os.walk("."):
    for _file in files:
        remote_path = "%s/%s" % (root, _file)
        if remote_path.startswith("."):
            remote_path = remote_path[1:] #.으로 시작하는 경로이면 .이후로 값을 변경한다.
        if os.path.splitext(_file)[1] not in filters:
            web_paths.put(remote_path) # 필터에 걸리지 않는 확장자라면 큐에 넣는다.
        
            
def test_remote():
    while not web_paths.empty():  #4) 
        path = web_paths.get()
        url = "%s%s" % (target, path)
        
        request = urllib2.Request(url)
        try:
            response = urllib2.urlopen(request)
            content = response.read()
            
            print "[%d] => %s" % (response.code, path)  #5)
            response.close()
            
        except urllib2.HTTPError as error:  #6) .htaccess file 설정등으로 블록되었을 때 
            print "Failed %s" % error.code
            pass

# 설정된 스레드 수만 큼 동작한다.
for i in range(threads):
        print "Spawning thread: %d" % i
        t = threading.Thread(target=test_remote)
        t.start()
        
        