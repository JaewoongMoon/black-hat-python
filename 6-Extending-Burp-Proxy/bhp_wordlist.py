#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Turing Website Content into Password Gold
# Many times, security comes down to one thing: user passwords. 
# It's sad but true. Making things worse, when it comes to 
# web applications, especially custom ones, it's all too common 
# to find that account lockouts aren't implemented. In other instances,
# strong passwords are not enforced. In these cases, an online password
# guessing session like the one in the last chapter might be just the 
# ticket to gain access to the site. 

# The trick to online password guessing is getting the right wordlist. 
# You can't test 10 million passwords if you're in a hurry, so you need
# to be able to create a wordlist targeted to the site in question. 
# Of course, there are scripts in the Kali Linux distribution that crawl
# a website and generate a wordlist based on site content. Though if you've
# already used Burp Spider to crawl the site, why send more traffic just to 
# generate a wordlist? Plus, those scripts usually have a ton of command-line
# argumentsmmand-line arguments to impress your friends, so let's make Burp 
# do the heavy lifting. 

from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import re
from datetime import datetime
from HTMLParser import HTMLParser

class TagStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.page_text = []
    
    def handle_data(self, data):
        self.page_text.append(data)
        
    def strip(self, html):
        self.feed(html)
        return " ".join(self.page_text)
    

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers   = callbacks.getHelpers()
        self.context    = None
        self.hosts      = set()
        
        # Start with something we know is common
        self.wordlist   = set(["password"])
        
        # we set up our extension
        callbacks.setExtensionName("BHP Wordlist")
        callbacks.registerContextMenuFactory(self)
        return 
        
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Create Wordlist", actionPerformed=self.wordlist_menu))
        
        return menu_list
    
    # 메뉴 클릭시 동작하는 핸들러 펑션 
    def wordlist_menu(self, event):
        
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()
        
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host         = http_service.getHost()
            
            self.hosts.add(host)
            
            http_response = traffic.getResponse()
            
            if http_response:
                self.get_words(http_response)
        self.display_wordlist()
        return 
    
    # HTTP Response 로부터 사이트 특정의 단어를 추출해주는 펑션
    def get_words(self, http_response):
        
        headers, body = http_response.tostring().split('\r\n\r\n', 1)
        
        # skip non-text responses
        if headers.lower().find("content-type: text") == -1:
            return 
        
        tag_stripper = TagStripper()
        page_text = tag_stripper.strip(body)
        
        words = re.findall("[a-zA-Z]\w{2,}", page_text)
        
        for word in words:
            
            # filter out long strings
            if len(word) <= 12:
                self.wordlist.add(word.lower())
        return 
    
    # 단어 뒤에 접미어를 붙여서 다양한 비밀번호 패턴을 만들어 낸다.
    def mangle(self, word):
        year     = datetime.now().year
        suffixes = ["", "1", "!", year]
        mangled = []
        
        for password in (word, word.capitalize()):
            for suffix in suffixes:
                mangled.append("%s%s" % (password, suffix))
                
        return mangled
    
    # 만들어진 단어 목록을 보여준다. 
    def display_wordlist(self):
        
        print "#! comment: BHP Wordlist for site(s) %s" % ", ".join(self.hosts)
        
        for word in sorted(self.wordlist):
            for password in self.mangle(word):
                print password
                
        return 
    