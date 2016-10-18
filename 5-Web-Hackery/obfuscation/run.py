# -*- coding: utf-8 -*-
import jjencode
from jjdecode import JJDecoder

a = '"/><script>alert("i love hacking~")</script>'
enc = jjencode.JJEncoder(a).encoded_text
print(enc)



#print(JJDecoder(enc).decode())
