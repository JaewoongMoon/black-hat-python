#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import paramiko
import subprocess

def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    # parameko 는 패스워드 인증이 아닌 키 인증도 지원한다. (주석부분)
    #client.load_host_keys('/root/.ssh/known_hosts')
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.exec_command(command)
        print ssh_session.recv(1024)
    return

# 192.168.56.101 서버에 SSH로 로그인해서 id 명령을 실행한 결과를 출력한다.
ssh_command('192.168.56.101', 'jwmoon', 'ted0201', 'id')