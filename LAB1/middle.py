#!/usr/bin/env python
"""Implementation of middleware for a p2p system with
a centralized Index/Certificate authority. Middleware enables
creation of public key infrastructure and data sharing/transport
system.
"""

import sys
import socket
import json

import requests
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Hash import MD5
from Crypto.Hash import SHA256

from utils import BUFFER_SIZE

class __Middleware(object):
	"""Super class for common methods of both middlewares."""

	def generate_rsa_key(self, rsa_bits, rsa_e):
		"""Generate a new pub/private rsa key pair object."""
		key = RSA.generate(rsa_bits, e=rsa_e)
		# pub_key = key.publickey().exportKey("PEM")
		# private_key = key.exportKey("PEM")

		return key

	def get_key_from_certificate(self, certificate):
		"""When received a certificate, get the public key
		from it without having to worry about the format of the
		certificate.
		"""
		text = '\n'.join(certificate.strip().split("\n")[3:])
		# print(text)
		key = RSA.importKey(text)
		return key

	def get_id_from_certificate(self, certificate):
		"""Get the ID from the certificate."""
		id_ = certificate.strip().split("\n")[2]
		return id_

	def verify_certificate(self, key, text):
		"""Verify certificate with a public key."""
		split_ = text.strip().split("\n")
		signature = split_[0]
		text = "\n".join(split_[1:])
		sig = long(signature)

		digest = SHA256.new(text).digest()
		return key.verify(digest, (sig, ))

	def recv_over_tcp(self, socket):
		"""Properly receive data over TCP socket."""
		response = socket.recv(8)
		# print("Got: " + response)		
		# first comes the size
		size = long(response[:response.find("@")])
		recvd = response[response.find("@")+1:]
		# print(recvd)
		while size > len(recvd):
			data = socket.recv(self.buffer_size)
			if not data:
				break
			recvd += data

		socket.sendall("OK")
		return recvd

	def send_over_tcp(self, socket, msg):
		# print("Sending: " + msg)
		size = len(msg)
		# print("Size " + str(size))
		socket.sendall(str(size) + "@")
		# print("sent size.")
		socket.sendall(msg)

		# receive ok status
		socket.recv(self.buffer_size)
		# response = s.recv(self.buffer_size)
		return

	def process_command(self):
		pass

class SPMiddleware(__Middleware):
	"""Class implements all the functionalities of the service provider middleware."""
	def __init__(self, host_ip, host_port, buffer_size, my_name, own_port):
		self.ip = host_ip
		self.port = host_port
		# self.id = my_id
		self.name = my_name
		self.own_port = own_port
		self.buffer_size = buffer_size

	def register_with_central(self):
		"""Register with central node in order to be recognized as a part of the network. 
		Returns ID obtained from CR.
		"""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.ip, self.port))
		msg = "register/" + str(self.name) + "/" + str(self.own_port)

		self.send_over_tcp(s, msg)
		# response = s.recv(self.buffer_size)
		response = self.recv_over_tcp(s)
		# print("ID obtained: ")
		# print(response)
		s.close()
		return response

	def request_certificate(self, id_, key):
		"""Request yourself a certificate from the host. Returns the certificate provided by CR."""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.ip, self.port))
		msg = "req_cer/" + id_ + "\n" + str(key)

		self.send_over_tcp(s, msg)
		# response = s.recv(self.buffer_size)
		response = self.recv_over_tcp(s)
		s.close()
		# id_ = self.get_id_from_certificate(response)
		return response

	def request_host_certificate(self, ip, port):
		"""Get a certificate of any other machine certificate."""
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		msg = "req_cer/"

		self.send_over_tcp(s, msg)
		# response = s.recv(self.buffer_size)
		response = self.recv_over_tcp(s)
		s.close()
		# id_ = self.get_id_from_certificate(response)
		return response

	def update_file_list(self, id_, files, ip, port):
		"""Method enables sending the file list to CR for indexing."""
		dump = json.dumps(files)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, port))
		msg = "update_files/" + str(id_) + "/" + str(dump)

		self.send_over_tcp(s, msg)
		# response = s.recv(self.buffer_size)
		# recv status
		self.recv_over_tcp(s)
		# we hope everything is okay
		s.close()

	def get_file_list(self):
		"""Uses http to get the file list from CR.
		Returns it as a dictionary.
		"""
		dump = requests.get("http://127.0.0.1:8000/files")
		files = json.loads(dump.content)
		return files

	def get_sp_list(self):
		"""Usess http to get the sp list from CR.
		Returns it as a dictionary.
		"""
		# print("In get sp")
		dump = requests.get("http://127.0.0.1:8000/providers")
		# print(dump.content)
		sps = json.loads(dump.content)
		return sps

	def fetch_file(self, file_id, id_, username, certificates, own_cert, own_key):
		"""Fetch a file with file_id or return None in case of error."""
		files = self.get_file_list()
		if file_id not in files:
			return None

		# try:
			# local fetch
		if id_ == files[file_id][2]:
			f = open(files[file_id][1][0], "r").read()
			return f
		else:
		# try fetching from remote SP
			# get the info
			return self.__remote_fetch(file_id, id_, username, files, certificates, 
				own_cert, own_key)
			# pass
		# except: return None

	def display_files(self, files):
		"""Display dictionary of files got from CR."""
		print("Files:")
		print("File_ID File_Name Author Info Location_ID")

		for key in sorted(files.iterkeys()):
			out = str(key)
			out += " " + files[key][0]
			out += " " + files[key][1][1]
			out += " " + files[key][1][2]
			out += " " + files[key][2]

			print(out)

	def display_sp_list(self, list):
		"""Display the list of SPs ordered by ID."""
		# key = ID, val = (name, address, port)
		print("Service providers:")
		print("ID name address port")

		for key in sorted(list.iterkeys()):
			out = str(key)
			out += " " + list[key][0]
			out += " " + list[key][1]
			out += " " + str(list[key][2])

			print(out)

	def process_command(self, own_id, addr, command, certificates, key, 
			certificate, files):
		"""Processes all the commands that come to an SP."""
		if command.startswith("req_sp_cer/"):
			print("HERE")
			# cert = command.split("/")[1].strip()
			cert = command[command.find("/")+1:]
			cr_cert = certificates["CR"]
			key = self.get_key_from_certificate(cr_cert)

			# print("Going to verify following certificate")
			# print(cert)
			# print("######")
			# print("Key: ")
			# print(key.publickey().exportKey("PEM"))

			status = self.verify_certificate(key, cert)
			if status == False:
				return "DENIED"

			# print("THERE")

			id_ = cert.strip().split("\n")[2]
			certificates[id_] = cert
			# print("OUCH")
			return certificate


		# else first check if ID is valid and if not, refuse the connection
		elif command.startswith("req_file/"):
			# command = command.split("/")
			command = command[command.find("/")+1:]
			id_ = command[:command.find("/")]
			if id_ not in certificates:
				return "DENIED"

			command = command[command.find("/")+1:]
			other_key = self.get_key_from_certificate(certificates[id_])

			msg = other_key.encrypt(command, 32)
			msg = msg[0]
			username = msg.strip().split("/")[0]
			filename = msg.strip().split("/")[1]

			if filename not in files:
				file_ = ""
			else:
				file_ = files[filename][0]
				file_ = open(file_, "r").read()

			msg = str(own_id) + "/" + username + "/" + filename + "/"
			msg += file_
			msg = key.decrypt(msg)
			return msg

		else:
			return "DENIED"

	def __remote_fetch(self, file_id, id_, username, file_list, 
			certificates, own_cert, own_key):
		"""Fetch a file from a remote node."""
		print ("FETCHING A FILE")
		other_id = str(file_list[file_id][2])
		# check if in certificates

		filename = file_list[file_id][0]
		sp_list = self.get_sp_list()

		ip = sp_list[other_id][1]
		port = str(sp_list[other_id][2])

		if other_id not in certificates:
			if self.__exchange_sp_certificate(ip, port, certificates, own_cert) == -1:
				print("Error fetching the certificate")
				sys.exit(1)

		print ("Certificates done")
		# make request
		msg = str(username) + "/" + str(filename)
		# key = self.get_key_from_certificate(certificates[other_id])
		msg = own_key.decrypt(msg)
		msg = "req_file/" + str(id_) + "/" + msg

		#send the request
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		self.send_over_tcp(s, msg)

		response = self.recv_over_tcp(s)
		other_key = self.get_key_from_certificate(certificates[other_id])
		response = other_key.encrypt(response, 32)
		# get file from response
		response = response[0]
		response = response[response.find("/")+1:]
		response = response[response.find("/")+1:]
		response = response[response.find("/")+1:]
		file_ = response

		# file_ = other_key.encrypt(file_)
		return file_

	def __exchange_sp_certificate(self, ip, port, certificates, certificate):
		"""If its communication with an SP for the first time, do certificate
		exchange.
		"""
		print ("Exchanging certs")
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		msg = "req_sp_cer/" + certificate
		self.send_over_tcp(s, msg)

		response = self.recv_over_tcp(s)
		s.close()

		if response == "DENIED":
			return -1

		# check certificate using CR pub key
		cr_cert = certificates["CR"]
		key = self.get_key_from_certificate(cr_cert)
		status = self.verify_certificate(key, response)
		if status == False:
			return -1

		id_ = response.strip().split("\n")[2]
		# print("ID obtained after exchange: " + str(id_))
		certificates[id_] = response
		return 1

class CRMiddleware(__Middleware):
	def __init__(self, providers, files, certificates, tcp_ip, tcp_port, buffer_size):
		self.providers = providers
		self.files = files
		self.certificates = certificates
		self.buffer_size = buffer_size
		self.ip = tcp_ip
		self.port = tcp_port

	def generate_certificate(self, other_id, key):
		"""Generates a certificate from ID and pub key."""
		certificate = "ID:" + str(MD5.new(str(Random.new().read(5))).hexdigest()) + "\n"

		certificate += other_id
		sig = self.sign_certificate(key, certificate)
		certificate = sig + "\n" + certificate

		return certificate

	def sign_certificate(self, key, text):
		"""Sign a text with a key using SHA256."""
		if not key.can_sign():
			return None

		digest = SHA256.new(text).digest()
		signature = key.sign(digest, None)[0]

		sig = str(signature)
		return sig

	def listen(self, key, certificate):
		"""Listen for incoming TCP connections."""
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.bind((self.ip, self.port))
		server_socket.listen(5)

		try:
			while True:
				conn, addr = server_socket.accept()
				print("Machine just connected: " + str(addr))

				msg = self.recv_over_tcp(conn)
				# print("Received: " + str(msg))
				msg = self.process_command(msg, addr, key, certificate)
				# print ("Sending back: " + str(msg))
				self.send_over_tcp(conn, msg)
				conn.close()

		except KeyboardInterrupt:
			server_socket.close()

	def process_command(self, command, addr, key, certificate):
		try:
			if command.startswith("req_cer/"):
				if command == "req_cer/":
					return certificate

				command = command[command.find("/")+1:]
				id_ = command.strip().split("\n")[0]
				other_key = command
				if id_ not in self.providers:
					# print("HERE")
					return "DENIED"

				cert = self.generate_certificate(other_key, key)
				self.certificates[id_] = cert

				return cert
			# SP is making its presence known
			elif command.startswith("register"):
				command = command.split("/")
				if len(command) < 3:
					return "Cancelled"
				# ID is the dict key
				id_ = len(self.providers)
				# key = ID, val = (name, address, port)
				self.providers[str(id_)] = (command[1], str(addr[0]), int(command[2]))
				return str(id_)

			elif command.startswith("update_files"):
				command = command[command.find("/")+1:]
				id_ = command[:command.find("/")]
				if id_ not in self.certificates:
					return "DENIED"

				dump = command[command.find("/")+1:]
				# print(dump)
				files = json.loads(dump)
				# print("THERE")
				for name in files:
					# if name) not in self.files:
					key = len(self.files)
					self.files[key] = (name, files[name], id_)
				return ("OK")

			else: return "Invalid"
				# else: return "ID already exists"
		except:
			return "DENIED"
