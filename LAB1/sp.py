#!/usr/bin/env python
"""Implements the service provider node in the p2p system.
SP nodes communicate with each other after they get a
proper certificate from the central authority.
"""

import sys
import socket
import threading
import Crypto

import middle
from utils import *

HOST_ADDR = '127.0.0.1'
HOST_PORT = 5007
MY_ID = '1'
MY_NAME = 'Computer 1'
# port on which all the other 
SP_ADDR = '127.0.0.1'
SP_PORT = 5030

class ServiceProvider(object):
	"""Class implements the service provider node in the p2p network."""
	def __init__(self, name, host_ip, host_port, own_ip, 
			own_port, buffer_size, file_list=None, user_dir=None):
		self.host_ip = host_ip
		self.host_port = host_port
		self.ip = own_ip
		self.port = own_port
		self.buffer_size = buffer_size
		self.name = name
		self.certificates = {}
		self.middle = middle.SPMiddleware(host_ip, host_port,self.buffer_size, name, self.port)

		self.key = self.middle.generate_rsa_key(RSA_BITS, RSA_E)
		self.public_key = self.key.publickey().exportKey("PEM")
		self.private_key = self.key.exportKey("PEM")

		#first steps
		# print("Registering")
		self.id = self.register()
		# print("Done")
		cert = self.middle.request_host_certificate(self.host_ip, self.host_port)
		self.certificates["CR"] = cert

		self.certificate = None
		self.certificate = self.get_certificate()
		self.username = ""

		# print(self.id)
		# print()
		# print("Certificate")
		# print(self.certificate)		

		# self.id = id_
		self.users = {}
		if file_list is not None:
			self.files = self.input_files(file_list)
			# report files
			self.report_files()
		else:
			self.files = {}

		if user_dir is not None:
			f = open(user_dir, "r")
			for line in f:
				line = line.strip().split()
				user = line[0]
				password = line[1]

				self.users[user] = password

	def user_login(self):
		"""Ask the user to login."""
		while True:
			print("Enter your username:")
			username = sys.stdin.readline().strip()
			# print(username)
			print("enter password:")
			password = sys.stdin.readline().strip()
			# print(password)

			if username not in self.users or password != self.users[username]:
				print("Wrong username/password.")
			else:
				self.username = username
				break
		return

	def register(self):
		"""Send a message about own existence to the central authority.
		Also send him the port on which you are listening for other SPs.
		"""
		return self.middle.register_with_central()

	def get_certificate(self):
		"""Request and get the certificate from the
		central authority node.
		"""	
		cert = self.middle.request_certificate(self.id, self.public_key)
		# self.certificate = cert
		return cert

	def input_files(self, files_path):
		"""Input all the file information given to in the files_path file."""
		files = {}
		with open(files_path, "r") as f:
			for line in f:
				line = line.strip().split()
				name = line[0]
				path = line[1]
				author = line[2]
				info = " ".join(line[3:])

				files[name] = (path, author, info)

		return files

	def report_files(self):
		"""Send own file list to CR."""
		self.middle.update_file_list(self.id, self.files, self.host_ip, self.host_port)

	# def wait(self):
	# 	"""Wait for the input from the user."""
	# 	try:
	# 		while True:
	# 			print("")
	# 			print("Waiting for input. <Ctrl+C> to end.")
	# 			print("Enter R to read file list.")
	# 			print("Enter O <file_id> to fetch and open a file.")
	# 			print("Enter L to read SP list.")
	# 			print("")

	# 			input_ = sys.stdin.readline()
	# 			input_ = input_.strip()
	# 			if input_ == "R":
	# 				cr_files = self.middle.get_file_list()
	# 				self.middle.display_files(cr_files)

	# 			elif input_.startswith("O"):
	# 					file_id = input_.strip().split()[1]
	# 					# print ("HERE")
	# 					# print (self.certificate)
	# 					f = self.middle.fetch_file(file_id, self.id, self.username, 
	# 						self.certificates, self.certificate, self.key)
	# 					if f == None:
	# 						print("File does not exist.")

	# 					else:
	# 						print("##################")
	# 						print(f)
	# 						print("##################")

	# 			elif input_ == "L":
	# 				sp_list = self.middle.get_sp_list()
	# 				self.middle.display_sp_list(sp_list)

	# 	except KeyboardInterrupt:
	# 		return

	# 	# except:
	# 	# 	print("Error. Exiting.")
	# 	# 	return

	# def listen(self):
	# 	"""This method is run by a separate thread and serves for listening to the incoming
	# 	SP connections.
	# 	"""

	# 	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 	server_socket.bind((self.ip, self.port))
	# 	server_socket.listen(5)

	# 	try:
	# 		while True:
	# 			conn, addr = server_socket.accept()
	# 			# print("Machine just connected: " + str(addr))

	# 			# msg = conn.recv(self.buffer_size)
	# 			msg = self.middle.recv_over_tcp(conn)
	# 			# print("Received: " + str(msg))
	# 			msg = self.middle.process_command(self.id, addr, msg, self.certificates, 
	# 				self.key, self.certificate, self.files)
	# 			# print ("Sending back: " + str(msg))
	# 			# conn.sendall(msg)
	# 			self.middle.send_over_tcp(conn, msg)
	# 			conn.close()

	# 	except KeyboardInterrupt:
	# 		server_socket.close()
	# 		return	

	def listen(self):
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind((self.ip, self.port))
		server_socket.listen(5)
		# yield

		while True:
			print("Here")
			conn, addr = server_socket.accept()
			# print("Machine just connected: " + str(addr))
			# msg = conn.recv(self.buffer_size)
			msg = self.middle.recv_over_tcp(conn)
			# print("Received: " + str(msg))
			msg = self.middle.process_command(self.id, addr, msg, self.certificates, 
				self.key, self.certificate, self.files)
			# print ("Sending back: " + str(msg))
			# conn.sendall(msg)
			self.middle.send_over_tcp(conn, msg)
			conn.close()
			# yield


	# def run(self):
	# 	"""Runs the Service provider. SP should always be run through this method."""
	# 	# print("HERE")
	# 	# print(self.certificate)
	# 	# t1 = threading.Thread(target=self.wait)
	# 	t2 = threading.Thread(target=self.listen)

	# 	t2.daemon = True
	# 	t2.start()
	# 	self.user_login()
	# 	# t1.daemon = True
	# 	# t1.start()

	# 	# t1.join()
	# 	t2.join()

# if __name__ == "__main__":
# 	if len(sys.argv) < 8:
# 		print("./script <name> <host_ip> <host_port> <own_ip> <own_port> <file_list> <users_dir>")
# 		raise ValueError("Not enough arguments.")

# 	name = sys.argv[1]
# 	host_ip = sys.argv[2]
# 	host_port = int(sys.argv[3])
# 	own_ip = sys.argv[4]
# 	own_port = int(sys.argv[5])
# 	file_list = sys.argv[6]
# 	users = sys.argv[7]

# 	buffer_size = BUFFER_SIZE

# 	sp = ServiceProvider(name, host_ip, host_port, own_ip, own_port, 
# 		buffer_size, file_list, users)
# 	sp.run()
