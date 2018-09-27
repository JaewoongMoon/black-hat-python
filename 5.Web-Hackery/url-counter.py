# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

url = 'http://alpha-blacksquad.hangame.co.jp'
source_code = requests.get(url)
plain_text = source_code.content
soup = BeautifulSoup(plain_text, 'lxml')
i = 1
hrefs = [] 

# get hrefs
for link in soup.select('a'):
    href = link.get('href')
    # validation check 
    if '#' == href or "javascript:" in href:
        continue
    
    title = link.string
    
    temp = href.split('?')
    if len(temp) > 1:
        href = temp[0]
    
    # add items    
    addable = True
    for item in hrefs:
        if item['url'] == href: # 같은것이 있다면
            addable = False
            break

    if addable:    
        hrefs.append({'url' : href, 'value' : title})

# print
for item in hrefs:
    href = item['url']
    title = item['value']
    if url == href[0:len(url)]:
        print('[%d]-[%s]-%s'%(i, href, title))
    
        i=i+1
    else:
        if href[0:4] == "http" or href.startswith('//'):
            print('Not Target Domain [%s]'%href)
        else:
            print('[%d]-[%s]-%s'%(i, href, title))
            i=i+1