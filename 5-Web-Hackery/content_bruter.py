#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib2
import threading
import Queue
import urllib

threads = 50
#target_url = "http://beta-shop.comico.jp"
target_url = "http://tf-techorus.cartstar.net"
wordlist_file = "all.txt"
resume = None
user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"

def build_wordlist(wordlist_file):
    
    # word list 파일에서 데이터를 읽어온다.
    fd = open (wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()
    
    found_resume = False
    words = Queue.Queue()   # word 를 저장할 큐 준비
    
    for word in raw_words:
        word = word.rstrip()
        
        if resume is not None: # 중복여부 판별
            
            if found_resume:
                words.put(word) # 발견한 단어를 큐에 넣는다.
            else:
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume
        else:
            words.put(word)
            
    return words
                    

# 큐의 데이터를 사용자 입맛에 맞게 조정한다.
def dir_bruter (word_queue, extensions=None):
    
    while not word_queue.empty(): # 파라메터 큐 loop
        attempt = word_queue.get()
        
        attempt_list = []
        
        # check to see if there is a file extension; if not,
        # it's a directory path we're bruting
        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)
            
        # if we want to bruteforce extensions
        if extensions:
            for extension in extensions: # extensions 아이템 개수만큼의 패턴추가
                attempt_list.append("/%s%s" % (attempt, extension))
                
        # iterate over our list of attempts
        for brute in attempt_list:
            url = "%s%s" % (target_url, urllib.quote(brute))
            
            try:
                headers = {}
                headers["User-Agent"] = user_agent
                req = urllib2.Request(url, headers=headers)
                response = urllib2.urlopen(req)
                
                if len(response.read()):
                    print "[%d] => %s" % (response.code, url)
                    
            except urllib2.URLError, e:
                
                if hasattr(e, 'code') and e.code != 404:
                    print "!!! %d => %s" % (e.code, url)
                
                pass
            

word_queue = build_wordlist(wordlist_file)            
extensions = [".php", ".jsp", ".do", ".bak"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue, extensions,))
    t.start()

