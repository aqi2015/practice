#!/usr/bin/env python
# coding:utf8

__author__ = 'aqi'

import socket
import threading


def server(s):
	while True:
		try :
			conn, addr = s.accept()
			handler(conn, addr)
		except socket.timeout:
			print 'time out'
		conn.close()


def handler(conn, addr):
	def input_name_passwd():
		conn.sendall('请输入登陆名: ')
		name = conn.recv(1024)
		conn.sendall('请输入登陆密码: ')
		passwd = conn.recv(1024)
		return name, passwd

	def login(myname):
		name, passwd = input_name_passwd()
		if name in Chat_user.user:
			if passwd == Chat_user.user.get(name):
				Chat_user.user_conn[name] = conn
				myname['myname'] = name
				return True
		else:
			conn.sendall('用户名或密码错误!\n')
			return False

	def register(myname):
		conn.sendall('新用户注册\n')
		name, passwd = input_name_passwd()
		if name in Chat_user.user:
			conn.sendall('该用户名已注册！\n')
			return False
		else:
			Chat_user.user[name] = passwd
			Chat_user.user_conn[name] = conn
			myname['myname'] = name
			return True

	myname = {}
	print 'Got connection from', addr
	choice = {'login': login, 'register': register}
	status = False
	while True:
		conn.settimeout(300)
		conn.sendall('请输入指令(login/register/exit):')
		data = conn.recv(1024).strip()

		if data in choice:
			status = choice[data](myname)
			if status:
				break
		elif data == 'exit':
			break
		else:
			conn.sendall('输入错误！\n')

	if status:
		myname = myname['myname']
		conn.sendall('登陆成功，欢迎进入聊天室！\n')
		try:
			while True:
				data = conn.recv(1024)
				if data:
					for user, other_conn in Chat_user.user_conn.items():
						if user is not myname:
							other_conn.sendall('recv: ' +  data)
		except:
			del(Chat_user.user_conn[myname])


class Chat_user(object):
	user = {}
	user_conn = {}


class thread(threading.Thread):

	def __init__(self, func, args=None, name=None):
		threading.Thread.__init__(self)
		self.name = name
		self.func = func
		self.args = args

	def run(self):
		apply(self.func, self.args)


def main():
	host = '0.0.0.0'
	port = 2000
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((host, port))
	s.listen(10)

	pool = [thread(server,(s,)) for i in xrange(10)]

	for th in pool:
		th.setDaemon(True)
		th.start()

	for th in pool:
		th.join()

if __name__ == '__main__':
	main()
