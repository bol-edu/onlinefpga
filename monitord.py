import threading
import paramiko
import requests
import os, time
import random
import string
import smtplib
from flask import Flask
from flask import request
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import *


app = Flask(__name__)
client = MongoClient(MongoIP, MongoPort)
db = client.boledudb
col_device = db.boledudevice
col_monitord = db.boledumonitord
PynqZ2List.sort()
Kv260List.sort()


def email_notification(receiver, title_txt, notification):
	msg = MIMEMultipart()
	msg['From'] = GmailSender
	msg['To'] = receiver
	msg['Subject'] = 'OnlineFPGA notification' + ' - ' + title_txt
	msg.attach(MIMEText(notification, 'plain'))
	text = msg.as_string()
	try:
		smtpserver = smtplib.SMTP(SmtpServer, SmtpPort)
		smtpserver.starttls()
		smtpserver.login(GmailSender, GmailPasswd)
		smtpserver.sendmail(GmailSender, receiver, text)
		smtpserver.close()
		return('send bat job email notification is successfully')
	except:
		return('send bat job email notification is unsuccessfully')			
		
		
def get_random_passwd(length):
	  # random string of lower case and upper case letters
    passwd_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return(passwd_str)
    
    
def find_internal_ip_port_by_device(device):
	for i in col_device.find({}, {"_id":0, 'device':1 , 'internal_ip':1, 'ssh_port':1}):
		if i['device'] == device:
			return(i['internal_ip'], i['ssh_port'])
	return('internal ip not found', 'ssh port not found')      
  

def find_external_ip_port_by_device(device):
	for i in col_device.find({}, {"_id":0, 'device':1 , 'external_ip':1, 'web_port':1}):
		if i['device'] == device:
			return(i['external_ip'], i['web_port'])
	return('external ip not found', 'web port not found')      


def find_web_passwd_by_device(device):
	for i in col_device.find({}, {"_id":0, 'device':1 , 'web_passwd':1}):
		if i['device'] == device:
			return(i['web_passwd'])
	return('web passwd not found')
	
	
def find_user_by_device(device):
	for i in col_device.find({}, {"_id":0, 'device':1 , 'user':1}):
		if i['device'] == device:
			return(i['user'])
	return('user count not found')
	
	
def find_board_by_device(device):
	for i in col_device.find({}, {"_id":0, 'device':1 , 'u50_board':1}):
		if i['device'] == device:
			return(i['u50_board'])
	return('u50_board not found')
	
	
def find_batch_count_email_by_device(device):
	for i in col_device.find({}, {"_id":0, 'device':1 , 'batch_count':1 , 'batch_email':1}):
		if i['device'] == device:
			return(i['batch_count'], i['batch_email'])
	return('batch_count and batch_email not found')	
	

def find_device_by_internal_ip(ip):
	for i in col_device.find({}, {"_id":0, 'device':1, 'internal_ip':1}):
		if i['internal_ip'] == ip:
			return(i['device'])
	return('device not found')
	
	
def find_device_by_ssh_port(port):
	for i in col_device.find({}, {"_id":0, 'device':1, 'ssh_port':1}):
		if i['ssh_port'] == port:
			return(i['device'])
	return('device not found')	
	
	
def find_timeup_by_email(email):
	for i in col_monitord.find({}, {"_id":0, 'email':1 , 'timeup':1}):
		if i['email'] == email:
			return(i['timeup'])
	return('timeup not found')
	
	
def find_device_by_email(email):
	for i in col_monitord.find({}, {"_id":0, 'email':1 , 'device':1}):
		if i['email'] == email:
			return(i['device'])
	return('device not found')
	
	
def validate_job_consistent(email, job):
	for i in col_monitord.find({}, {"_id":0, 'email':1, 'job':1}):
		if i['email'] == email:
			if i['job'] == job:				
				return(True)				
	return(False)	


def find_key_idx_of_dictionary(dictionary, key):
	return(list(dictionary).index(key))
	
		
def get_rented_record(email):
	for i in col_monitord.find():
		if email == i['email']:
			return (i) 
	return ('the user has no rent record ')	
		
		
def get_batch_email_by_device(device):
	email = ''
	for i in col_device.find({}, {"_id":0, 'device':1, 'batch_email':1}):
		if device == i['device']:			
			try:
				email = i['batch_email'][0]
			except:
				pass
	return(email)				
	
	
def query_batch_job_by_email(email, init_wait):
	rented_record = get_rented_record(email)
	query_job_count = 0
	query_jobs = ''
	for i in rented_record['job_list']:
		query_job_count = query_job_count + 1
		if not init_wait:
			query_jobs = query_jobs + str(query_job_count).zfill(2) + ' ' + 'batch job: ' + i + ', ' + 'status: ' + rented_record['job_list'][i] + '\n'
		else:
			query_jobs = query_jobs + str(query_job_count).zfill(2) + ' ' + 'batch job: ' + i + ', ' + 'status: ' + 'wait' + '\n'
	return(query_job_count, query_jobs)


def update_tenant():
	alluser = str.split(os.popen('ls ' + U50UserHome).read())
	for i in U50List:
		tenant_count = 0
		for j in alluser:
			if i + '.' in j:			
				tenant_count = tenant_count + 1
		col_device.update_one({'device':'u50_'+i},{ '$set':{'tenant':tenant_count}})		
					
	
def init_ssh_passwd(rented_record):
	ssh_passwd = ""
	if 'no rent record' in str(rented_record):
		ssh_passwd = ""
	else:	
		ssh_passwd = rented_record['ssh_passwd']
	if ssh_passwd == "":
		ssh_passwd = get_random_passwd(PasswdLength)
	return(ssh_passwd)
	

def gen_u50_ssh_passwd(ssh_passwd, device):
	numbered = False
	for i in U50List:
		if i in ssh_passwd:
			numbered = True
	ssh_passwd = device.replace('u50_', '') +	'.' + ssh_passwd if not numbered else ssh_passwd
	return(ssh_passwd)
	
	
def gen_batch_title_txt(rented_record):
	total_jobs = len(rented_record['job_list'])
	finish_jobs = 0
	for i in rented_record['job_list']:
		if rented_record['job_list'][i] == 'finish':
			finish_jobs = finish_jobs + 1
	title_txt = str(finish_jobs) + '/' + str(total_jobs) + ' ' + 'batch jobs finished'
	return(title_txt)

							
def find_queue_email_by_device(device):
	email = ''
	for i in col_device.find({}, {"_id":0, 'device':1, 'queue_email':1}):
		if device == i['device']:			
			try:
				email = i['queue_email'][0]
			except:
				pass
	return(email)
	
	
def update_queue_timeout(device, timeout):
	for i in col_device.find({}, {"_id":0, 'device':1}):
		if device == i['device']:
			col_device.update_one({'device':i['device']},{'$set':{ 'queue_timeout':timeout}})
	return('update queue timeout is finishing ')
	

def alias_to_vck5k(device):
	if 'u50' in device:
		device_idx = int(device.replace('u50_', ''))
		if device_idx <= len(U50Alias) and not U50Alias[device_idx-1] == '':
			return(U50Alias[device_idx-1])
	return(device)	


def find_external_ip():
	mrt_result = str.split(os.popen('timeout 0.75 mtr -m 2 -p www.google.com' ).read())	
	if ExternalIPBakGateway in mrt_result:
		return(ExternalIPBak)
	return(ExternalIP)
		
					
def reset_pynq(ip, pynq_home, USERNAME, PASSWORD, port, web_passwd):
	try:	
		res_device = find_device_by_internal_ip(ip) if MonitordInLab == True else find_device_by_ssh_port(port)
		device = res_device if not 'not found' in res_device else ''
		col_device.update_one({'device':device},{ '$set':{'status':'unknown'}})
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())		
		client.connect(hostname=ip, username=USERNAME, password=PASSWORD, port=port)
		sftp = client.open_sftp()		
		sftp.put('./' + PynqResetFile, pynq_home + PynqResetFile)
		print('[2008] connect_to_pynq(): ' + 'sftp from %s to %s %s' %('./' + PynqResetFile, device, pynq_home + PynqResetFile))
		sftp.close()		
		print('[2009] connect_to_pynq(): ' + 'ssh to %s with %s:%s to set web passwd %s and restart jupyter notebook' %(device, ip, port, web_passwd))
		device_type = 'pynq' if pynq_home == PynqZ2Home else 'kv260'
		stdin, stdout, stderr = client.exec_command(PynqPython3 + ' ' + pynq_home + PynqResetFile + ' ' + web_passwd + ' ' + device_type)
		time.sleep(2)
		client.exec_command('rm -f ' + pynq_home + PynqResetFile)
		col_device.update_one({'device':device},{ '$set':{'status':'available'}})
		col_device.update_one({'device':device},{ '$set':{'web_passwd':web_passwd}})		
		out = stdout.read().decode().strip()
		client.close()		
	except:
		col_device.update_one({'device':device},{ '$set':{'status':'unknown'}})
		print('[2010] connect_to_pynq(): ' + 'ssh to %s with %s:%s unsuccessfully' %(device, ip, port))	
	return('reset jupyper web passwd is finishing')


def detect_u50(ip, port):
	try:
		res_device = find_device_by_internal_ip(ip) if MonitordInLab == True else find_device_by_ssh_port(port)
		device = res_device if not 'not found' in res_device else ''
		nc_result = str.split(os.popen(NcCommand + ' ' + ip + ' ' + port).read())
		time.sleep(2)
		if len(nc_result) == 2:
			status = 'unknown'
			user = find_user_by_device(device)			
			if not 'user count not found' in str(user):
				if user == U50UserLimit:
					col_device.update_one({'device':device},{ '$set':{'status':'used'}})
					status = 'used'		
				if user < U50UserLimit:
					col_device.update_one({'device':device},{ '$set':{'status':'available'}})
					status = 'available'	
				print('[2011] detect_to_u50(): ' + 'nc to %s with %s:%s and set status to %s successfully' %(device, ip, port, status))
		else:
			col_device.update_one({'device':device},{ '$set':{'status':'unknown'}})
			print('[2012] detect_to_u50(): ' + 'nc to %s with %s:%s unsuccessfully' %(device, ip, port))
	except:
		col_device.update_one({'device':device},{ '$set':{'status':'unknown'}})
		print('[2013] detect_to_u50(): ' + 'nc to %s with %s:%s unsuccessfully' %(device, ip, port))	
	return('detect u50 is finishing')	
    

def manage_u50_user(ip, device, port, manage_act, username, job, timeupstr):
	try:		
		if not job == 'u50_batch':
			col_device.update_one({'device':device},{ '$set':{'status':'unknown'}})
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		device_id = device.replace('u50_', '')
		for i in range(len(U50UserNameList)):
			if device_id in U50UserNameList[i]:
				USERNAME = U50UserNameList[i]
		for i in range(len(U50UserPassWordList)):
			if device_id in U50UserPassWordList[i]:
				PASSWORD = U50UserPassWordList[i]		
		client.connect(hostname=ip, username=USERNAME, password=PASSWORD, port=port)		
		stdin, stdout, stderr = client.exec_command('echo ' + PASSWORD + ' | sudo -S ' + U50Python3 + ' ' + U50ManageUserHome + U50ManageUserFile + \
		                                            ' ' + manage_act + ' ' + username + ' ' + job + ' ' + timeupstr.replace(' ', '_'))
		client.close()
		print('[2014] manage_u50_user(): ' + 'ssh to %s with %s:%s to %s user %s with job %s successfully' %(device, ip, port, manage_act, username, job))
		time.sleep(2)		
		update_tenant()		
		user = find_user_by_device(device)
		u50_board = find_board_by_device(device)
		email = find_queue_email_by_device(device)
		if not 'user count not found' in str(user):
			if manage_act == 'add':
				col_device.update_one({'device':device},{ '$set':{'user':user+1}})
				user = user + 1
				if job == 'u50_validation':
					col_device.update_one({'device':device},{ '$set':{'u50_board':u50_board-1}})
			if manage_act == 'del':
				col_device.update_one({'device':device},{ '$set':{'user':user-1}})
				user = user - 1
				if job == 'u50_validation':
					col_device.update_one({'device':device},{ '$set':{'u50_board':u50_board+1}})
			if user == U50UserLimit:
				col_device.update_one({'device':device},{ '$set':{'status':'used'}})
			if user < U50UserLimit:
				col_device.update_one({'device':device},{ '$set':{'status':'available'}})	
			if U50QueueEnable and not email == '' and manage_act == 'del':
				timeup = datetime.now() + timedelta(minutes=U50QueueTimeOut)
				update_queue_timeout(device, timeup.strftime('%m/%d/%Y %H:%M:%S'))				
				title_txt = 'device ' + alias_to_vck5k(device) + ' is available now, your rent reservation is timeout at ' + timeup.strftime('%m/%d %H:%M:%S')				
				email_notification(email, title_txt, '')
	except:
		col_device.update_one({'device':device},{ '$set':{'status':'unknown'}})
		print('[2015] manage_u50_user(): ' + 'ssh to %s with %s:%s to %s %s with job %s unsuccessfully' %(device, ip, port, manage_act, username, job))
		return('manage u50 user is not finishing')
	return('manage u50 user is finishing')		


def dispatch_job_brabber(email, device, job_act, job_path):
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		device_id = device.replace('u50_', '')
		for i in range(len(U50UserNameList)):
			if device_id in U50UserNameList[i]:
				USERNAME = U50UserNameList[i]
		for i in range(len(U50UserPassWordList)):
			if device_id in U50UserPassWordList[i]:
				PASSWORD = U50UserPassWordList[i]
		internal_ip, ssh_port = find_internal_ip_port_by_device(device)
		ip = internal_ip if MonitordInLab == True else find_external_ip()
		client.connect(hostname=ip, username=USERNAME, password=PASSWORD, port=ssh_port)
		stdin, stdout, stderr = client.exec_command('echo ' + PASSWORD + ' | sudo -S ' + U50Python3 + ' ' + U50ManageUserHome + U50JobGrabberFile + ' ' \
		                                            + job_act + ' ' + email + ' ' + job_path)
		time.sleep(2)
		client.close()
		print('[5006] dispatch_job_brabber(): ' + ' dispatch user %s batch job %s to device %s of ip port %s with job action %s successfully' \
		      %(email, job_path, device, ip + ':' + ssh_port, job_act))
	except:
		print('[5007] dispatch_job_brabber(): ' + ' dispatch user %s batch job %s to device %s unsuccessfully' %(email, job_path, device))
	return('dispatch job brabber is finishing')
			
    
def fpga_init_db():
	
	queue_timeout = []	
	queue_user = []
	queue_email = []
	batch_count = []
	batch_email = []
	for i in U50List:
		for j in col_device.find():
			if 'u50_' + i in j['device']:
				queue_timeout.append(j['queue_timeout'])
				queue_user.append(j['queue_user'])
				queue_email.append(j['queue_email'])
				batch_count.append(j['batch_count'])
				batch_email.append(j['batch_email'])
	
	tenant = []	
	alluser = str.split(os.popen('ls ' + U50UserHome).read())
	for i in U50List:
		tenant_count = 0
		for j in alluser:
			if i + '.' in j:
				tenant_count = tenant_count + 1
		tenant.append(tenant_count)				
			
	for i in ['^pynq', '^kv260', '^u50']:
		allquery = { 'device': {'$regex': i} }
		col_device.delete_many(allquery)
	
	external_ip = find_external_ip()
					
	init_pynq_record = []
	for i in range(len(PynqZ2List)):
                  web_passwd = get_random_passwd(PasswdLength)
                  pynq_type = 'pynq_' if int(PynqZ2List[i]) <= PynqZUStartBase else 'pynqzu_'
                  pynq_id = PynqZ2List[i] if int(PynqZ2List[i]) <= PynqZUStartBase else str(int(PynqZ2List[i])-PynqZUStartBase).zfill(2)
                  init_pynq_record.append({'device':pynq_type+pynq_id, 'status':'unknown', \
		  	                  'internal_ip':InternalSec+'1'+PynqZ2List[i],'external_ip':external_ip, \
		  	                  'web_port':'2'+PynqZ2List[i]+'00', 'ssh_port':'1'+PynqZ2List[i]+'00', 'web_passwd':web_passwd})
                  col_device.insert_one(init_pynq_record[i])
                  print('[0001] fpga_init(): set device init status to %s' %(init_pynq_record[i]))
	
	init_kv260_record = []
	for i in range(len(Kv260List)):
		  web_passwd = get_random_passwd(PasswdLength)
		  init_kv260_record.append({'device':'kv260_'+Kv260List[i], 'status':'unknown', \
		  	                  'internal_ip':InternalSec+str(50+int(Kv260List[i])),'external_ip':external_ip, \
		  	                  'web_port':str((60+int(Kv260List[i]))*100), 'ssh_port':str((50+int(Kv260List[i]))*100), 'web_passwd':web_passwd})
		  col_device.insert_one(init_kv260_record[i])
		  print('[0002] fpga_init(): set device init status to %s' %(init_kv260_record[i]))
	
	if not len(U50List) == len(batch_count):
		print('[0003] fpga_init(): mismatch init u50 data')
	init_u50_record = []	  
	for i in range(len(U50List)):		  
		  init_u50_record.append({'device':'u50_'+U50List[i], 'status':'unknown', \
		  	                  'internal_ip':InternalSec+'1'+U50List[i].lstrip('0'),'external_ip':external_ip, \
		  	                  'web_port':'', 'ssh_port':'1'+U50List[i].lstrip('0')+'00', 'web_passwd':'', 'user':0, 'queue_user':queue_user[i], \
		  	                  'u50_board':U50BoardAvailable[i], 'tenant':tenant[i], 'queue_timeout':queue_timeout[i], 'queue_email':queue_email[i], \
		  	                  'batch_count':batch_count[i], 'batch_email':batch_email[i]})
		  col_device.insert_one(init_u50_record[i])
		  print('[0004] fpga_init(): set device init status to %s' %(init_u50_record[i]))
			
	pynq_threads = []
	for i in range(len(PynqZ2List)):
		ip = init_pynq_record[i]['internal_ip'] if MonitordInLab == True else external_ip	
		ssh_port = DefaultSSHPort if MonitordInLab == True else init_pynq_record[i]['ssh_port']
		pynq_threads.append(threading.Thread(target = reset_pynq, args = (ip, PynqZ2Home, PynqUserName, PynqUserPasswd, \
		                    ssh_port, init_pynq_record[i]['web_passwd'],)))		
		pynq_threads[i].start()
	
	kv260_threads = []
	for i in range(len(Kv260List)):
		ip = init_kv260_record[i]['internal_ip'] if MonitordInLab == True else external_ip	
		ssh_port = DefaultSSHPort if MonitordInLab == True else init_kv260_record[i]['ssh_port']
		kv260_threads.append(threading.Thread(target = reset_pynq, args = (ip, Kv260Home, Kv260UserName, Kv260UserPasswd, \
		                    ssh_port, init_kv260_record[i]['web_passwd'],)))		
		kv260_threads[i].start()
		
	u50_threads = []
	for i in range(len(U50List)):
		ip = init_u50_record[i]['internal_ip'] if MonitordInLab == True else external_ip	
		ssh_port = init_u50_record[i]['ssh_port']
		u50_threads.append(threading.Thread(target = detect_u50, args = (ip, ssh_port,)))
		u50_threads[i].start()
	return('init fpga device status in mongodb is finishing')
	

def check_timeup():
	pynq_threads = []
	kv260_threads = []
	u50_tasks = []
	u50_batch_jobs = []
	for i in col_monitord.find():
		if not '00:00:00' ==  i['timeup'] and datetime.now() > datetime.strptime(i['timeup'], '%m/%d/%Y %H:%M:%S'):			
			print('[2001] check_and_action(): ' + 'triggered by timeup detection, the user %s has device %s timeup at %s' %(i['email'], i['device'], i['timeup']))
			col_monitord.update_one({'email':i['email']},{ '$set':{'timeup':'00:00:00'}})
			web_passwd = get_random_passwd(PasswdLength)   
			internal_ip, ssh_port = find_internal_ip_port_by_device(i['device'])
			ip = internal_ip if MonitordInLab == True else find_external_ip()
			if not 'not found' in internal_ip:
				if 'pynq' in i['device']:
					print('[2002] check_and_action(): ' + 'triggered by timeup detection, try reset device %s to web passwd %s' %(i['device'], web_passwd))					
					ssh_port = DefaultSSHPort if MonitordInLab == True else ssh_port
					pynq_threads.append(threading.Thread(target = reset_pynq, args = (ip, PynqZ2Home, PynqUserName, PynqUserPasswd, ssh_port, web_passwd,)))
				if 'kv260' in i['device']:
					print('[2003] check_and_action(): ' + 'triggered by timeup detection, try reset device %s to web passwd %s' %(i['device'], web_passwd))					
					ssh_port = DefaultSSHPort if MonitordInLab == True else ssh_port
					kv260_threads.append(threading.Thread(target = reset_pynq, args = (ip, Kv260Home, Kv260UserName, Kv260UserPasswd, ssh_port, web_passwd,)))	
				if 'u50' in i['device']:
					print('[2004] check_and_action(): ' + 'triggered by timeup detection, try del user %s on device %s' %(i['ssh_passwd'], i['device']))
					internal_ip, ssh_port = find_internal_ip_port_by_device(i['device'])					
					u50_tasks.append({'ip':ip, 'device':i['device'], 'port':ssh_port, 'manage_act':'del', 'username':i['ssh_passwd'], 'job':i['job']})
					print('[2005] check_and_action(): ' + U50RentedLogFile + ' written: ' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ' ' + i['email'] + ' returned ' + i['device'])
					os.system('echo ' + '\'' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ' ' + i['email'] + ' returned ' + alias_to_vck5k(i['device']) + '\'' + ' >> ' + U50RentedLogFile)	
					if 'u50_batch' in i['job']:
						u50_batch_jobs.append(i['email'])
			else:
				print('[2006] check_and_action(): ' + 'get internal ip and ssh port from device mongodb unsuccessfully')
	for i in pynq_threads:
		i.start()	
	for i in kv260_threads:
		i.start()	
	for i in u50_batch_jobs:
		res_request = requests.post(MonitordJobUpdateRequest, json = {'jobber':'kill', 'email':i})		
		print('[2007] check_and_action(): ' + 'triggered by timeup detection, %s' %(res_request.text))
	for i in u50_tasks:
		manage_u50_user(i['ip'], i['device'], i['port'], i['manage_act'], i['username'], i['job'], '00:00:00')
	
	if U50QueueEnable:
		for i in col_device.find():
			if 'u50' in i['device'] and not '00:00:00' ==  i['queue_timeout'] and datetime.now() > datetime.strptime(i['queue_timeout'], '%m/%d/%Y %H:%M:%S'):				
				update_queue_email = i['queue_email']
				update_queue_email.pop(0)
				col_device.update_one({'device':i['device']},{'$set':{ 'queue_email':update_queue_email}})
				col_device.update_one({'device':i['device']},{'$set':{ 'queue_user':i['queue_user']-1}})
				col_device.update_one({'device':i['device']},{'$set':{ 'queue_timeout':'00:00:00'}})
				email = find_queue_email_by_device(i['device'])
				if not email == '':
					timeup = datetime.now() + timedelta(minutes=U50QueueTimeOut)
					update_queue_timeout(i['device'], timeup.strftime('%m/%d/%Y %H:%M:%S'))
					title_txt = 'device ' + alias_to_vck5k(i['device']) + ' is available now, your rent reservation is timeout at ' + timeup.strftime('%m/%d %H:%M:%S')
					email_notification(email, title_txt, '')
	return('check timeup is finishing')
	

def check_batch_job(device):
	email = get_batch_email_by_device(device)
	rented_record = get_rented_record(email)
	if not 'no rent record' in str(rented_record):
		if not rented_record['timeup'] == '00:00:00' and rented_record['job'] == 'u50_batch' and not rented_record['job_list'] == {}:
			for j in rented_record['job_list']:
				if rented_record['job_list'][j] == 'wait':
					batch_run = False
					idx = list(rented_record['job_list']).index(j)
					if idx > 0:
						dic_key = list(rented_record['job_list'])[idx-1]
						if rented_record['job_list'][dic_key] == 'finish' or rented_record['job_list'][dic_key] == 'kill' or rented_record['job_list'][dic_key] == 'error':
							batch_run = True
					else:
						batch_run = True
					if batch_run == True:
						job_list = rented_record['job_list']
						job_list.update({j:'start'})
						col_monitord.update_one({'email':email},{ '$set':{ 'job_list':job_list } })						
						print('[5008] check_batch_job(): ' + 'dispatch a wait batch job %s with status start of user %s to device %s' %(j, rented_record['email'], rented_record['device']))
						dispatch_job_brabber(rented_record['email'], rented_record['device'], 'run', j)
						timeup = datetime.now() + timedelta(minutes=RentedU50JobMinutes)
						retimeupstr =  timeup.strftime('%m/%d %H:%M:%S')
						col_monitord.update_one({'email':email},{'$set':{'timeup':retimeupstr}})
						title_txt = 'start ' + str(idx+1).zfill(2) + ' batch job and timeout at ' + retimeupstr
						query_job_count, notification = query_batch_job_by_email(email, False)
						email_notification(rented_record['email'], title_txt, notification)
						break
	return('check batch job is finishing')
	

def check_batch_queue():	
	for i in col_device.find({}, {"_id":0, 'device':1}):
		if 'u50' in i['device']:
			keep_user_inqueue = False
			email = get_batch_email_by_device(i['device'])
			rented_record = get_rented_record(email)
			if not 'no rent record' in str(rented_record) and not rented_record['job_list'] == {}:
				for j in rented_record['job_list']:
					if rented_record['job_list'][j] in ['wait', 'start', 'run']:
						keep_user_inqueue = True
				if not keep_user_inqueue:
					for j in col_device.find({}, {"_id":0, 'device':1}):
						if j['device'] == rented_record['device']:
							break
					batch_count, batch_email = find_batch_count_email_by_device(j['device'])
					batch_email.pop(0)
					col_device.update_one({'device':j['device']},{ '$set':{ 'batch_count':batch_count-1 } })
					col_device.update_one({'device':j['device']},{ '$set':{ 'batch_email':batch_email } })
					print('[5009] check_batch_queue(): ' + 'remove a user %s from batch queue on device %s' %(email, i['device']))									
					title_txt = gen_batch_title_txt(rented_record)					
					query_job_count, notification = query_batch_job_by_email(email, False)
					email_notification(rented_record['email'], title_txt, notification)
					print('[5010] check_batch_queue(): ' + 'email %s to user %s' %(title_txt, email))
					res_request = requests.post(MonitordReturnRequest, json = {'email':email, 'device':j['device'], 'job':'u50_batch'})
					print('[5011] check_batch_queue(): %s' %(res_request.text))					
	return('check batch queue is finishing')	

	
def retry_ssh_connection(status, device):
	pynq_threads = []
	kv260_threads = []
	external_ip = find_external_ip()
	if status == 'unknown':
		for i in col_device.find():
			if ('pynq' in i['device'] or 'kv260' in i['device']) and i['status'] == 'unknown':
				print('[1002] retry_ssh(): ' + 'triggered by %s ssh detection, the device %s has %s status' %(status, i['device'], status))
				web_passwd = get_random_passwd(PasswdLength)
				internal_ip, ssh_port = find_internal_ip_port_by_device(i['device'])
				print('[1003] retry_ssh(): ' + 'triggered by %s ssh detection, try reset device %s to web passwd %s' %(status, i['device'], web_passwd))
				ip = internal_ip if MonitordInLab == True else external_ip
				ssh_port = DefaultSSHPort if MonitordInLab == True else ssh_port
				if 'pynq' in i['device']:
					pynq_threads.append(threading.Thread(target = reset_pynq, args = (ip, PynqZ2Home, PynqUserName, PynqUserPasswd, ssh_port, web_passwd,)))
				else:
					kv260_threads.append(threading.Thread(target = reset_pynq, args = (ip, Kv260Home, Kv260UserName, Kv260UserPasswd, ssh_port, web_passwd,)))						
	if status == 'available':
		for i in col_device.find():
			if i['status'] == 'available' and i['device'] == device:
				print('[1004] retry_ssh(): ' + 'triggered by %s ssh detection, the device %s has %s status' %(status, i['device'], status))
				web_passwd = get_random_passwd(PasswdLength)
				internal_ip, ssh_port = find_internal_ip_port_by_device(i['device'])
				print('[1005] retry_ssh(): ' + 'triggered by %s ssh detection, try reset device %s to web passwd %s' %(status, i['device'], web_passwd))
				ip = internal_ip if MonitordInLab == True else external_ip
				ssh_port = DefaultSSHPort if MonitordInLab == True else ssh_port
				if 'pynq' in i['device']:
					pynq_threads.append(threading.Thread(target = reset_pynq, args = (ip, PynqZ2Home, PynqUserName, PynqUserPasswd, ssh_port, web_passwd,)))
				else:
					kv260_threads.append(threading.Thread(target = reset_pynq, args = (ip, Kv260Home, Kv260UserName, Kv260UserPasswd, ssh_port, web_passwd,)))						
	for i in pynq_threads:
		i.start()
	for i in kv260_threads:
		i.start()	
	return('retry ssh connection is finishing')
	
	
def retry_nc_connection(status, device):
	u50_threads = []
	external_ip = find_external_ip()
	if status == 'unknown':
		for i in col_device.find():
			if 'u50' in i['device'] and i['status'] == 'unknown':
				print('[1006] retry_nc(): ' + 'triggered by %s nc detection, the device %s has %s status' %(status, i['device'], status))
				internal_ip, ssh_port = find_internal_ip_port_by_device(i['device'])
				print('[1007] retry_nc(): ' + 'triggered by %s nc detection, try nc to device %s' %(status, i['device']))
				ip = internal_ip if MonitordInLab == True else external_ip
				u50_threads.append(threading.Thread(target = detect_u50, args = (ip, ssh_port,)))
	if status == 'available':
		for i in col_device.find():
			if i['status'] == 'available' and i['device'] == device:
				print('[1008] retry_nc(): ' + 'triggered by %s nc detection, the device %s has %s status' %(status, i['device'], status))
				internal_ip, ssh_port = find_internal_ip_port_by_device(i['device'])
				print('[1009] retry_nc(): ' + 'triggered by %s nc detection, try nc to device %s' %(status, i['device']))
				ip = internal_ip if MonitordInLab == True else external_ip
				u50_threads.append(threading.Thread(target = detect_u50, args = (ip, ssh_port,)))
	for i in u50_threads:
		i.start()
	return('retry nc connection is finishing')	
						

@app.route('/fpga_init', methods = ['GET', 'POST'])
def fpga_init():
	current_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	print('[0000] fpga_init(): initialize device status in mongodb at %s' %(current_time))
	fpga_init_db()
	return('fpga_init is finishing')


@app.route('/retry_unknown', methods = ['GET', 'POST'])
def retry_unknown():	
	current_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	print('[1000] retry_unknown(): retry unknown ssh and nc connection at %s' %(current_time))
	retry_ssh_connection('unknown', '')
	retry_nc_connection('unknown', '')
	return('retry_unknown is finishing')
	
	
@app.route('/retry_available', methods = ['GET', 'POST'])
def retry_available():
	data = request.json
	current_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	print('[1001] retry_available(): retry available ssh and nc connection at %s' %(current_time))
	if 'pynq' in data['device'] or 'kv260' in data['device']:
		retry_ssh_connection('available', data['device'])	
	if 'u50' in data['device']:
		retry_nc_connection('available', data['device'])
	return('retry_available is finishing')	
	

@app.route('/check_and_action', methods = ['GET', 'POST'])
def check_and_action():
	current_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	print('[2000] check_and_action(): monitord checks whether a timeup rent at %s' %(current_time))
	check_timeup()
	check_batch_queue()
	u50_batch_threads = []
	for i in U50List:
		device = 'u50_' + i
		u50_batch_threads.append(threading.Thread(target = check_batch_job, args = (device,)))
	for i in u50_batch_threads:
		i.start()	
	return('check_and_action is finishing')
	

@app.route('/batch_jobber', methods = ['GET', 'POST'])
def batch_jobber():
	data = request.json	
	if data['jobber'] == 'request':
		batch_request = False
		device = ''
		for i in col_monitord.find():
			if data['email'] == i['email'] and not i['timeup'] == '00:00:00':
				batch_request = True
				device = i['device']
				job_list= {}				
				for j in data['job_list']:
					job_list.update({j:'wait'})										
				update_record = {'$set': {'email':i['email'], 'device':i['device'], 'job':i['job'], 'job_list':job_list, 'external_ip_port':i['external_ip_port'], \
					               'web_passwd':i['web_passwd'], 'ssh_passwd':i['ssh_passwd'], 'timeup':i['timeup'], 'rent_time':i['rent_time'], 'used_count':i['used_count']}}
				rented_record = get_rented_record(data['email'])
				col_monitord.update_one(rented_record, update_record)		
		if batch_request:
			title_txt =  str(len(data['job_list'])) + ' ' + 'batch jobs received'
			query_job_count, notification = query_batch_job_by_email(data['email'], True)
			email_notification(data['email'], title_txt, notification)
			print('[5000] batch_jobber(): ' + 'email %s to user %s' %(notification, data['email']))
			print('[5001] batch_jobber(): user %s request batch jobs %s on device %s successfully' %(data['email'], job_list, device))
			return('user %s request batch jobs successfully' %(data['email']))
		else:
			print('[5002] batch_jobber(): user %s request batch jobs on device %s unsuccessfully' %(data['email'], device))
			return('user %s request batch jobs unsuccessfully' %(data['email']))			
	elif data['jobber'] == 'update':
		rented_record = get_rented_record(data['email'])
		job_list= rented_record['job_list']
		job_list.update({data['job_list'][0]: data['status']})
		col_monitord.update_one({'email':data['email']},{ '$set':{ 'job_list':job_list } })
		print('[5003] batch_jobber(): job_grabber update user %s batch job %s with status %s on device %s' %(data['email'], data['job_list'][0], data['status'], rented_record['device']))
	elif data['jobber'] == 'query':
		rented_record = get_rented_record(data['email'])
		query_job_count, query_jobs = query_batch_job_by_email(data['email'], False)
		print('[5004] batch_jobber(): user %s query batch jobs %s on device %s' %(data['email'], rented_record['job_list'], rented_record['device']))
		return('user %s query %s batch jobs on device %s\n%s' %(data['email'], query_job_count, alias_to_vck5k(rented_record['device']), query_jobs))
	elif data['jobber'] == 'kill':
		rented_record = get_rented_record(data['email'])
		kill_job_count = 0
		kill_jobs = ''
		for i in rented_record['job_list']:
			if not rented_record['job_list'][i] == 'finish' and not rented_record['job_list'][i] == 'error':
				dispatch_job_brabber(data['email'], rented_record['device'], 'kill', i)
				print('[5005] batch_jobber(): user %s kill batch job %s on device %s' %(data['email'], i, rented_record['device']))
				kill_job_count = kill_job_count + 1
				kill_jobs = kill_jobs + 'batch job: ' + i + '\n'
		if not kill_job_count == 0:
			title_txt = gen_batch_title_txt(rented_record)
			query_job_count, notification = query_batch_job_by_email(data['email'], False)
			email_notification(rented_record['email'], title_txt, notification)
		return('user %s kill %s batch jobs on device %s\n%s' %(data['email'], kill_job_count, alias_to_vck5k(rented_record['device']), kill_jobs))
	else:
		pass
	return('batch jobber is finishing')

	
@app.route('/fpga_rent', methods = ['GET', 'POST'])
def fpga_rent():
	data = request.json
	print('[3000] fpga_rent(): received request: %s at %s' %(data, datetime.now().strftime('%m/%d/%Y %H:%M:%S')))
	rented_record = get_rented_record(data['email'])
	new_monitord_record = True if 'no rent record' in str(rented_record) else False
	pynq_or_kv260_rent_successfully = False	
	u50_rent_successfully = False
	u50_batch_successfully = False
	manage_u50_user_conn = ''	
	rent_timestr = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	timeup_pynq = datetime.now() + timedelta(minutes=RentedPynqMinutes)
	timeup_kv260 = datetime.now() + timedelta(minutes=RentedKv260Minutes)
	timeup_vitis = datetime.now() + timedelta(minutes=RentedVitisMinutes)
	timeup_u50 = datetime.now() + timedelta(minutes=RentedU50Minutes)
	timeup_u50_batch = datetime.now() + timedelta(hours=RentedU50BatchHours*U50BatchLimit)
	timeup_vck5k = datetime.now() + timedelta(minutes=RentedVCK5KMinutes)
	timeup = timeup_pynq if 'pynq' in data['device'] else timeup_kv260 if 'kv260' in data['device'] else \
	         timeup_vitis if 'vitis_tool' == data['job'] else \
	         timeup_vck5k if 'u50_validation' == data['job'] and '05' in data['device'] else \
	         timeup_u50 if 'u50_validation' == data['job'] else timeup_u50_batch
	timeupstr = timeup.strftime('%m/%d/%Y %H:%M:%S')
	if not data['job'] == 'u50_batch' and datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M') < datetime.strptime(ServiceStop, '%H:%M') and \
	   datetime.strptime(timeup.strftime('%H:%M'), '%H:%M') >= datetime.strptime(ServiceStop, '%H:%M'):
	   	timeuphm = datetime.strptime(ServiceStop, '%H:%M') + timedelta(minutes=-1)
	   	timeuphmstr = timeuphm.strftime('%H:%M')
	   	timeupstr = timeup.strftime('%m/%d/%Y') + ' ' + timeuphmstr + ':00'	   	
	if not data['job'] == 'u50_batch' and datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M') >= datetime.strptime(ServiceStop, '%H:%M') and \
	   datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M') <= datetime.strptime(ServiceStart, '%H:%M'):
	   	timeupstr = datetime.now().strftime('%m/%d/%Y %H:%M:%S')	   	
	external_ip, web_port = find_external_ip_port_by_device(data['device'])
	internal_ip, ssh_port = find_internal_ip_port_by_device(data['device'])
	web_passwd = find_web_passwd_by_device(data['device'])
	u50_account = get_random_passwd(PasswdLength)
	ip = internal_ip if MonitordInLab == True else find_external_ip()
	ssh_passwd = init_ssh_passwd(rented_record)	
	
	if 'pynq' in data['device'] or 'kv260' in data['device']:		
		if new_monitord_record:
			new_record = {'email':data['email'], 'device':data['device'], 'job':data['job'], 'job_list':{}, 'external_ip_port':external_ip + ':' + web_port, \
				            'web_passwd':web_passwd, 'ssh_passwd':ssh_passwd, 'account':'', 'timeup':timeupstr, 'rent_time':rent_timestr, 'used_count':1}
			col_device.update_one({'device':data['device']},{ '$set':{ 'status':'used' } })
			col_monitord.insert_one(new_record)
			pynq_or_kv260_rent_successfully = True
		elif rented_record['timeup'] == '00:00:00':
			update_record = {'$set': {'email':data['email'], 'device':data['device'], 'job':data['job'], 'job_list':{}, 'external_ip_port':external_ip + ':' + web_port, \
				               'web_passwd':web_passwd, 'ssh_passwd':ssh_passwd, 'account':'', 'timeup':timeupstr, 'rent_time':rent_timestr, 'used_count':rented_record['used_count']+1}}
			col_device.update_one({'device':data['device']},{ '$set':{ 'status':'used' } })
			col_monitord.update_one(rented_record, update_record)
			pynq_or_kv260_rent_successfully = True
		else:
			pass	
		if pynq_or_kv260_rent_successfully:
			rent_message = 'user %s rented device %s successfully\njupyter web ip port is %s, web passwd is %s and timeup at %s'
			print('[3001] fpga_rent(): ' + rent_message %(data['email'], data['device'], external_ip + ':' + web_port, web_passwd, timeupstr))
			return(rent_message %(data['email'], data['device'], external_ip + ':' + web_port, web_passwd, timeupstr))
		else:
			rent_message = 'user %s rented device %s unsuccessfully, already have used device/batch jobs?'
			print('[3002] fpga_rent(): ' + rent_message %(data['email'], data['device']))
			return(rent_message %(data['email'], data['device']))	
				
	if 'u50' in data['device']:
		ssh_passwd = gen_u50_ssh_passwd(ssh_passwd, data['device'])
		if new_monitord_record or rented_record['timeup'] == '00:00:00':
			if data['device'].replace('u50_', '') in ssh_passwd:
				manage_u50_user_conn = manage_u50_user(ip, data['device'], ssh_port, 'add', ssh_passwd, data['job'], timeupstr)
		u50_rent_successfully = True if 'u50 user is finishing' in manage_u50_user_conn else False		
						
		if u50_rent_successfully:
			if new_monitord_record:
				new_record = {'email':data['email'], 'device':data['device'], 'job':data['job'], 'job_list':{}, 'external_ip_port':external_ip + ':' + ssh_port, \
					            'web_passwd':'', 'ssh_passwd':ssh_passwd, 'account':'', 'timeup':timeupstr, 'rent_time':rent_timestr, 'used_count':1}
				col_monitord.insert_one(new_record)			
			elif rented_record['timeup'] == '00:00:00':
				update_record = {'$set': {'email':data['email'], 'device':data['device'], 'job':data['job'], 'job_list':{}, 'external_ip_port':external_ip + ':' + ssh_port, \
					               'web_passwd':'', 'ssh_passwd':ssh_passwd, 'account':rented_record['account'], 'timeup':timeupstr, 'rent_time':rent_timestr, 'used_count':rented_record['used_count']+1}}
				col_monitord.update_one(rented_record, update_record)				
			else:
				pass
			print('[3005] fpga_rent(): ' + U50RentedLogFile + ' written: ' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ' ' + data['email'] + ' rented ' + data['device'])
			os.system('echo ' + '\'' + datetime.now().strftime('%Y/%m/%d %H:%M:%S') + ' ' + data['email'] + ' rented ' + alias_to_vck5k(data['device']) + '\'' + ' >> ' + U50RentedLogFile)	
			if data['job'] == 'u50_validation':
				rent_message = 'user %s rented device %s successfully\nssh ip port is %s, ssh username/passwd is %s and timeup at %s'
				print('[3003] fpga_rent(): ' + rent_message %(data['email'], data['device'], external_ip + ':' + ssh_port, ssh_passwd, timeupstr))
				return(rent_message %(data['email'], alias_to_vck5k(data['device']), external_ip + ':' + ssh_port, ssh_passwd, timeupstr))
			if data['job'] == 'u50_batch':
				rent_message = 'user %s requested batch jobs successfully\nssh ip port is %s, ssh username/passwd is %s\nthe batch jobs progress will be notified by email'
				print('[3004] fpga_rent(): ' + rent_message %(data['email'], external_ip + ':' + ssh_port, ssh_passwd))
				return(rent_message %(data['email'], external_ip + ':' + ssh_port, ssh_passwd, data['job']))			
		else:
			if data['job'] == 'u50_validation':
				rent_message = 'user %s rented device %s unsuccessfully, already have used device/batch jobs or you are invalid tenant?'
				print('[3005] fpga_rent(): ' + rent_message %(data['email'], data['device']))
				return(rent_message %(data['email'], alias_to_vck5k(data['device'])))
			if data['job'] == 'u50_batch':
				rent_message = 'user %s requested batch jobs on device %s unsuccessfully, already have used device/batch jobs?'
				print('[3006] fpga_rent(): ' + rent_message %(data['email'], data['device']))
				rent_message = 'user %s requested batch jobs unsuccessfully, already have used device/batch jobs?'
				return(rent_message %(data['email']))
												

@app.route('/fpga_return', methods = ['GET', 'POST'])
def fpga_return():
	data = request.json
	current_time = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
	print('[4000] fpga_return(): user %s want to return device %s to finish rented session at %s' %(data['email'], data['device'], current_time))
	timeup = find_timeup_by_email(data['email'])
	device = find_device_by_email(data['email'])
	job_consistent = validate_job_consistent(data['email'], data['job'])
	timeup = timeup if not 'not found' in timeup else ''
	device = device if not 'not found' in device else ''	
	if not timeup == '00:00:00' and device == data['device'] and job_consistent:
		changed_timeup = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
		col_monitord.update_one({'email':data['email']},{ '$set':{ 'timeup':changed_timeup}})
		print('[4001] fpga_return(): change user %s timeup from %s to %s' %(data['email'], timeup, changed_timeup))
		if data['job'] == 'u50_batch':
			batch_count, batch_email = find_batch_count_email_by_device(device)
			try:
				batch_email.remove(data['email'])
				col_device.update_one({'device':data['device']},{ '$set':{ 'batch_count':batch_count-1 } })
				col_device.update_one({'device':data['device']},{ '$set':{ 'batch_email':batch_email } })
			except:
				pass		
			print('[4002] fpga_return(): remove user %s job %s from device %s' %(data['email'], data['job'], data['device']))	
			return ('user %s cancel bat jobs successfully' %(data['email']))
		else:
			return ('user %s return device %s successfully' %(data['email'], alias_to_vck5k(data['device'])))
	else:
		print('[4003] fpga_return(): change user %s timeup from %s to %s' %(data['email'], timeup, timeup))
		if data['job'] == 'u50_batch':			
			return ('user %s cancel bat jobs unsuccessfully' %(data['email']))	
		else:
			return ('user %s return device %s unsuccessfully' %(data['email'], alias_to_vck5k(data['device'])))	

    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
