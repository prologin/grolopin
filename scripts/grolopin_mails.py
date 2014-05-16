import json, os, subprocess

users = json.load(open('users.json'))
for ip in users:
	print users[ip]['email']
