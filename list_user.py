import os, sys
from pymongo import MongoClient
from config import *


client = MongoClient(MongoIP, MongoPort)
db = client.boledudb
col_user = db.boleduuser
col_monitord = db.boledumonitord


def list_user(find_type, key):
	user_number = 0
	if find_type == 'all':
		print('all registered users')
		for i in col_user.find({}, {"_id":0, 'email': 1, 'name': 1, 'date': 1}):
			print (i)
			user_number = user_number + 1
	elif find_type == 'dump':
		print('dump all registered users')
		for i in col_user.find({}, {"_id":0, 'email': 1}):
			print (i['email'])
			user_number = user_number + 1
		print ('\n')
		for i in col_user.find({}, {"_id":0, 'name': 1}):
			print (i['name'])
		print ('\n')
		for i in col_user.find({}, {"_id":0, 'date': 1}):
			print (i['date'])					
	elif find_type == 'online':
		print('all online users')
		for i in col_monitord.find({}, {"_id":0, 'email': 1, 'device': 1, 'timeup': 1, 'used_count': 1, 'rent_time': 1}):
			if i['timeup'] != '00:00:00':
				print (i)
				user_number = user_number + 1	
	elif find_type == 'rent_date':
		print('all users with rent_date' + ' ' + '\'%s\'' %(key))
		tmp_list = []
		for i in col_monitord.find({}, {"_id":0, 'rent_time': 1}):
			if key in i['rent_time']:
				tmp_list.append(i['rent_time'])
				user_number = user_number + 1
		tmp_list.sort()
		for i in range(len(tmp_list)):
			for j in col_monitord.find({}, {"_id":0, 'email': 1, 'device': 1, 'rent_time': 1}):
				if tmp_list[i] == j['rent_time']:
					print (j)					
	elif find_type == 'monitord':
		print('all users with monitord record' + ' ' + '\'%s\'' %(key))
		for i in col_monitord.find({}, {"_id":0, 'email': 1, 'device': 1, 'job':1, 'job_list':1, 'ssh_passwd':1, 'account':1, 'timeup':1, 'rent_time': 1}):
			if key in i['email'] or key in i['device'] or  key in i['ssh_passwd'] or  key in i['job']:
				print (i)
				user_number = user_number + 1
	else:
		print('all users with keyword' + ' ' + '\'%s\'' %(key))
		if not 'pynq' in key and not 'vitis' in key and not 'u50' in key and not 'batch' in key:
			for i in col_user.find({}, {"_id":0, 'email': 1, 'name': 1, 'password': 1, 'date': 1}):
				if key in i['email'] or key in i['name'] or key in i['password'] or key in i['date']:
					print (i)
					user_number = user_number + 1
		if 'pynq' in key or 'vitis' in key or 'u50' in key or 'batch' in key:
			for i in col_monitord.find({}, {"_id":0, 'email': 1, 'device': 1, 'job': 1, 'rent_time': 1}):
				if key in i['device'] or key in i['job']:
					print (i)
					user_number = user_number + 1		
	print('Total users: %s\n' %(user_number))
	print('\n')


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Usage:')
		print('python3 list_user.py all')
		print('python3 list_user.py dump')
		print('python3 list_user.py online')		
		print('python3 list_user.py rent_date \'keyword\'')
		print('python3 list_user.py monitord \'keyword\'')
		print('python3 list_user.py filter \'keyword\'')		
		print('\n')
		sys.exit()
	
	find_type = sys.argv[1]
	key = ''
	if find_type == 'all' or find_type == 'online' or find_type == 'dump' or \
	   find_type == 'rent_date' or find_type == 'monitord' or find_type == 'filter':
		if find_type == 'rent_date' or find_type == 'monitord' or find_type == 'filter':
			try:
				key = sys.argv[2]
			except:
				print('invalid keyword')
				sys.exit() 
	else:
		print('invalid argument')
		sys.exit()	
		
	list_user(find_type, key)