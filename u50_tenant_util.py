import os, sys
from config import *


def get_device_passwd():
	hostname = os.popen('hostname').read().rstrip('\n')
	device_id = hostname.replace('HLS', '')
	passwd = ''
	for i in range(len(U50UserPassWordList)):
		if device_id in U50UserPassWordList[i]:
			passwd = U50UserPassWordList[i]
	return(device_id, passwd)


def update_tenant(col_device):
	alluser = str.split(os.popen('ls ' + U50UserHome).read())
	for i in U50List:
		tenant_count = 0
		for j in alluser:
			if i + '.' in j:			
				tenant_count = tenant_count + 1
		col_device.update_one({'device':'u50_'+i},{ '$set':{'tenant':tenant_count}})
				
				
def list_tenant():
	alluser = str.split(os.popen('ls ' + U50UserHome).read())
	for i in U50List:
		tenant = []		
		tenant_count = 0
		for j in alluser:
			if i + '.' in j:
				tenant_info = str.split(os.popen('stat ' + U50UserHome + j).read())
				idx = tenant_info.index('Change:', 0)
				tenant.append(j + ' ' + 'change: ' + tenant_info[idx+1])
				tenant_count = tenant_count + 1
		print('Tenants on %s:' %('HLS'+i))
		for j in tenant:
			print(j)
		print('Total tenants: %s\n' %(tenant_count))								


def checkdb_tenant():
	from pymongo import MongoClient
	client = MongoClient(MongoIP, MongoPort)
	db = client.boledudb
	col_monitord = db.boledumonitord	
	alluser = str.split(os.popen('ls ' + U50UserHome).read())
	for i in U50List:
		tenant = []		
		unknown_tenant_count = 0
		for j in alluser:
			if i + '.' in j:
				tenant_info = str.split(os.popen('stat ' + U50UserHome + j).read())
				idx = tenant_info.index('Change:', 0)
				found_tenantdb = False
				for k in col_monitord.find({}, {"_id":0, 'ssh_passwd': 1}):
					if j == k['ssh_passwd']:
						found_tenantdb = True				
				if not found_tenantdb:
					tenant.append(j + ' ' + 'change: ' + tenant_info[idx+1])
					unknown_tenant_count = unknown_tenant_count + 1
		print('Tenants on %s not in monitord:' %('HLS'+i))
		for j in tenant:
			print(j)
		print('Total unknown tenants: %s\n' %(unknown_tenant_count))
		

def del_tenant(users):	
	device_id, hls_passwd = get_device_passwd()
	if '00' == device_id:
		print('tenant %s is not created on %s' %(users, 'HLS' + device_id))
		return(0)
	alluser = str.split(os.popen('ls ' + U50UserHome).read())
	del_tenant = []
	detail_del_tenant = []
	if users == 'all':
		for i in alluser:
			if device_id + '.' in i:
				del_tenant.append(i)
				tenant_info = str.split(os.popen('stat ' + U50UserHome + i).read())
				idx = tenant_info.index('Change:', 0)
				detail_del_tenant.append(i + ' ' + 'change: ' + tenant_info[idx+1])
		print('Del tenants on %s:' %('HLS'+device_id))
		for i in detail_del_tenant:
			print(i)		
		confirm = input('please confirm to del above tenants? (y/n)\n>> ')
		if confirm == 'y' or confirm == 'Y':			
			for i in del_tenant:
				os.system('echo %s | sudo -S killall -w -u %s' %(hls_passwd, i))
				os.system('echo %s | sudo -S userdel %s' %(hls_passwd, i))
				os.system('echo %s | sudo -S rm -rf %s%s' %(hls_passwd, U50UserHome, i))				
				print('del tenant %s on %s' %(i, 'HLS' + device_id))
		else:
			pass	
	else:
		if device_id in users:
			print('Del tenants on %s:' %('HLS'+device_id))
			tenant_info = str.split(os.popen('stat ' + U50UserHome + users).read())
			idx = tenant_info.index('Change:', 0)				
			print(users + ' ' + 'change: ' + tenant_info[idx+1])				
			confirm = input('please confirm to del the tenant? (y/n)\n>> ')
			if confirm == 'y' or confirm == 'Y':
				os.system('echo %s | sudo -S killall -w -u %s' %(hls_passwd, users))
				os.system('echo %s | sudo -S userdel %s' %(hls_passwd, users))
				os.system('echo %s | sudo -S rm -rf %s%s' %(hls_passwd, U50UserHome, users))
				print('del %s on %s' %(users, 'HLS' + device_id))
			else:
				pass
		else:
			print('tenant %s is not created on %s' %(users, 'HLS' + device_id))		
				

def deldb(users):
	from pymongo import MongoClient
	client = MongoClient(MongoIP, MongoPort)
	db = client.boledudb
	col_monitord = db.boledumonitord	
	col_device = db.boledudevice
	if users == 'all':		
	  deldb_list = []
	  for i in U50List:
	  	for j in col_monitord.find({}, {"_id":0, 'ssh_passwd': 1}):
	  		if i + '.' in j['ssh_passwd']:
	  			deldb_list.append(j['ssh_passwd'])        
	  for i in deldb_list:
	  	print(i)		
	  confirm = input('please confirm to deldb all? (y/n)\n>> ')
	  if confirm == 'y' or confirm == 'Y':
	  	for i in deldb_list:
	  		col_monitord.update_one({'ssh_passwd':i},{'$set':{'timeup':'00:00:00'}})
	  		col_monitord.update_one({'ssh_passwd':i},{'$set':{'ssh_passwd':''}})
	  		print('deldb %s (ssh_passwd field)' %(i))
	  	update_tenant(col_device) 
	  else:
	  	pass		
	else:
		print('deldb %s' %(users))
		confirm = input('please confirm to deldb? (y/n)\n>> ')
		if confirm == 'y' or confirm == 'Y':
			col_monitord.update_one({'ssh_passwd':users},{'$set':{'timeup':'00:00:00'}})
			col_monitord.update_one({'ssh_passwd':users},{'$set':{'ssh_passwd':''}})
			print('deldb %s (ssh_passwd field)' %(users))
			update_tenant(col_device)
		else:
			pass	
	

if __name__ == '__main__':	
	if len(sys.argv) < 2:
		print('Usage:')
		print('python3 u50_tenant.py list')
		print('python3 u50_tenant.py checkdb')
		print('python3 u50_tenant.py del all')
		print('python3 u50_tenant.py del account')		
		print('python3 u50_tenant.py deldb all')		
		print('python3 u50_tenant.py deldb account')
		print('\n')
		sys.exit()
	op = sys.argv[1]	
	if op == 'list' or op == 'checkdb' or op == 'del' or op == 'deldb':
		if op == 'list':
			list_tenant()
		elif op == 'checkdb':
			if not '00' in os.popen('hostname').read().rstrip('\n'):
				print('checkdb only run on management server')
				sys.exit()
			else:
				checkdb_tenant()
		elif op == 'del':
			try:
				del_tenant(sys.argv[2])
			except:
				print('invalid argument')
				sys.exit()
		else:			
			if not '00' in os.popen('hostname').read().rstrip('\n'):
				print('deldb only run on management server')
				sys.exit()
			try:
				deldb(sys.argv[2])
			except:
				print('invalid argument')
				sys.exit()									
	else:
		print('invalid argument')
		sys.exit()	
		