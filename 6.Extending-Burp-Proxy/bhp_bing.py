#!/usr/bin/python
# -*- coding: UTF-8 -*-

from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64
bing_api_key = "YOURKEY"

class BurpExtender(IBurpExtender, IContextMenuFactory):
    
    # @Implement IBurpExtender.registerExtenderCallbacks
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None
        
        # we set up our extension
        callbacks.setExtensionName("BHP Bing")
        callbacks.registerContextMenuFactory(self)
        return
    
    # Burp 메뉴에 Send to Bing 을 추가하고, 선택되었을 때 bing_menu함수를 호출하는 이벤트를 바인딩한다.
    # @Implement IContextMenuFactory.createMenuItems
    def createMenuItems(self, contextMenu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list
    
    
    def bing_menu(self, event):
        
        # grab the details of what the user clicked
        http_traffic = self.context.getSelectedMessages()
        
        print "%d requests highlighted" % len(http_traffic)
        
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host         = http_service.getHost()
            print "User selected host: %s" % host
            self.bing_search(host)
        return
    
    def bing_search(self, host):
        # check if we have an IP or hostname
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)
        
        if is_ip:
            ip_address = host
            domain     = False
        else:
            ip_address = socket.gethostbyname(host)
            domain     = True
            
        bing_query_string = "'ip:%s'" % ip_address
        self.bing_query(bing_query_string)
        
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)
            
    def bing_query(self, bing_query_string):
        print "Performing Bing search: %s" % bing_query_string
        
        # encode our query
        quoted_query = urllib.quote(bing_query_string)
        
        http_request = "GET https://api.datamarket.azure.com/Bing/Search/Web?$.format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request += "Connection: close\r\n"
        http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request += "User-Agent: Blackhat Python\r\n\r\n"
        
        json_body = self._callbacks.makeHttpRequest("api.datamarket.azure.com", 443, True, http_request).toString()
        
        json_body = json_body.split("\r\n\r\n", 1)[1] # 응답으로부터 헤더를 분리한다.
        
        try:
            r = json.loads(json_body) # json parsing
            
            if len(r["d"]["results"]):
                for site in r["d"]["results"]:
                    
                    print "*" * 100
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print "*" * 100
                    
                    j_url = URL(site['Url'])
                    
            if not self._callbacks.isInScope(j_url): # 발견한 사이트가 Burp의 target scope에 들어있지 않으면
                print "Adding to Burp scope"
                self._callbacks.includeInScope(j_url)
        except:
            print "No results from Bing"
            pass
        
        return
# Burp's HTTP API requires that we build up the entire HTTP requests as a string before sending it off, 
# and in particular you can see that we need to base64-encode our Bing API key and use HTTP basic
# authentication to make the API call. We then send our HTTP request to the Microsoft servers. 
# When the response returns, we'll have the entire response including the headers, 
# so we split the headers off and then pass it to our JSON parser 
# For each set of results, we output some information about the site that we discovered
# and if the discovered site is not in Burp's target scope, we automatically add it. 
# This is a great blend of using the Jython API and pure Python in a Burp extension to do additional recon
# work when attacking a particular target. 

                    
            
            