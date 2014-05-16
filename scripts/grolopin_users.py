import json, os, subprocess

def retrieve_birthyears():
	users = json.load(open('users.json'))
	for ip in users:
		os.system('echo "' + users[ip]['name'] + ' ' + users[ip]['email'] + '" >> uid.csv')
		os.system('mysql -u prologin -pPASSWORD USERNAME -e "SELECT users.uid, name, mail, substr(value, -7, 4) annee FROM users, profile_values WHERE users.uid = profile_values.uid AND profile_values.fid = 5 AND name = \'' + users[ip]['name'] + '\' AND mail != \'' + users[ip]['email'] + '\'" -Bs >> uid.csv')

retrieve_birthyears()
