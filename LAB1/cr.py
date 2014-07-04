#!/usr/bin/env python
"""Module stores the class that implements CR node in the p2p network."""

import sys
import socket
import BaseHTTPServer
import json
import threading

import middle
from utils import *

class CentralRegister(object):
	"""Implements the central register/certificate authority
	for the p2p system.
	"""
	def __init__(self, tcp_ip, tcp_port, buffer_size, rsa_e, rsa_bits):
		self.ip = tcp_ip
		self.port = tcp_port
		self.buffer_size = buffer_size
		self.providers = {}
		self.files = {}
		self.certificates = {}
		self.id = "CR"
		self.middle = middle.CRMiddleware(self.providers, self.files, 
			self.certificates, tcp_ip, tcp_port, self.buffer_size)

		self.key = self.middle.generate_rsa_key(rsa_bits, rsa_e)
		self.public_key = self.key.publickey().exportKey("PEM")
		self.private_key = self.key.exportKey("PEM")
		self.certificate = self.middle.generate_certificate(
			self.id + "\n" + self.public_key, self.key)
		print("I am server, my certificate:\n" + self.certificate)

class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path == "/providers":
				p = json.dumps(ca.providers)

			elif self.path == "/files":
				p = json.dumps(ca.files)
			else:
				self.send_error(404, "wrong request")
				return

			self.send_response(200)
			self.send_header('Content-type','json')
			self.end_headers()
			self.wfile.write(p)
			return

		except IOError:
			self.send_error(404, "wrong request")
			return			
		except KeyboardInterrupt:
			return

def run(ca, http):
	t1 = threading.Thread(target=ca.middle.listen, args=(ca.key, ca.certificate))
	t2 = threading.Thread(target=httpd.serve_forever)

	t1.daemon = True
	t1.start()
	t2.daemon = True
	t2.start()

	t1.join()
	t2.join()	

if __name__ == "__main__":
	ca = CentralRegister(TCP_IP, TCP_PORT, BUFFER_SIZE, RSA_E, RSA_BITS)
	server_addr = ('127.0.0.1', HTTP_PORT)
	httpd = BaseHTTPServer.HTTPServer(server_addr, HTTPHandler)

	run(ca, httpd)
