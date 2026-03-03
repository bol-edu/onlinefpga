import os, sys
import re
import requests
import random
import string
import smtplib
from pymongo import MongoClient
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import *


client = MongoClient(MongoIP, MongoPort)
db = client.boledudb
col_user = db.boleduuser
col_device = db.boledudevice
col_monitord = db.boledumonitord


def find_in_col_user(document):
	res = col_user.find(document, {})
	results = []
	for i in res:
		results.append(i)
	return results	


def check_device_exist(device):
	for i in col_device.find({}, {"_id":0, 'device':1}):
		if device == i['device']:
			return ('device is existing')
	return('device is not existing')


def alias_to_vck5k(device):
	if 'u50' in device:
		device_idx = int(device.replace('u50_', ''))
		if device_idx <= len(U50Alias) and not U50Alias[device_idx-1] == '':
			return(U50Alias[device_idx-1])
	return(device)


def alias_to_u50(device):
	if device in U50Alias:
		alias_device = 'u50_' + str(U50Alias.index(device)+1).zfill(2)
		for i in col_device.find({}, {"_id":0, 'device':1}):
			if alias_device == i['device']:
				return (alias_device)
	return('device is not existing')


def check_device_available(device):
	for i in col_device.find({}, {"_id":0, 'device':1, 'status':1, 'user':1}):
		if device == i['device']:
			if 'pynq' in device or 'kv260' in device:
				if i['status'] == 'available':
					return ('device is available')
			if 'u50' in device:
				if i['user'] < U50UserLimit:
					return ('device is available')
	return('device is not available')
	

def check_device_used(device):
	for i in col_device.find({}, {"_id":0, 'device':1, 'status':1, 'user':1}):
		if device == i['device']:
			if 'pynq' in device or 'kv260' in device:
				if i['status'] == 'used':
					return ('device is used')
			if 'u50' in device:
				if i['user'] > 0:
					return ('device is used')
	return('device is not used')
	
	
def check_device_status(device):
	for i in col_device.find({}, {"_id":0, 'device':1, 'status':1}):
		if device == i['device']:
			return (i['status'])
	return('unknown')					
	
	
def get_random_passwd(length):
	  # random string of lower case and upper case letters
    passwd_str = ''.join(random.choice(string.digits) for i in range(length))
    return(passwd_str)
    
    	
def check_email_invalid(email):
	try: 
		email = validate_email(email).email
	except EmailNotValidError as e:
		return(str(e))	
	
	
def check_email_exist(email):
	for i in col_user.find():
		if email == i['email']:
			return('email is already registered in Boledu foundation') 
	return('email is available.')	
	
	
def send_code_by_email(generated_code, receiver, name, password):
	msg = MIMEMultipart()
	message = 'user name: ' + name + '\n' + 'user passwd: ' + password
	msg['From'] = GmailSender
	msg['To'] = receiver
	msg['Subject'] = 'OnlineFPGA validation code' + ' - ' + generated_code 
	msg.attach(MIMEText(message, 'plain'))
	text = msg.as_string()
	try:
		smtpserver = smtplib.SMTP(SmtpServer, SmtpPort)
		smtpserver.starttls()
		smtpserver.login(GmailSender, GmailPasswd)
		smtpserver.sendmail(GmailSender, receiver, text)
		smtpserver.close()
		return('send validation code email is successfully')
	except:
		return('send validation code email is failed')
	
	
def check_email_passwd(email, password):
  exist = find_in_col_user({'email': email})
  if(len(exist) > 0):
  	#check if the password is correct
    correct = find_in_col_user({'email': email, 'password': password})
    if(len(correct) > 0):
      return('boledu user authentication pass')        			      
    else:
    	return('password %s is incorrect' %(password))
  else:
  	return('email %s is not existing' %(email))

	
def list_device(device_type):
	print('all online device boards')
	for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1}):
		if 'pynq_' in str(i) and not (device_type == 'kv260' or device_type == 'u50' or device_type == 'vck5k'):
			print (str(i).replace('\'status', '  \'status'))
	for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1}):
		if 'pynqzu' in str(i) and not (device_type == 'kv260' or device_type == 'u50' or device_type == 'vck5k'):
			print (str(i))		
	for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1}):
		if 'kv260' in str(i) and not (device_type == 'pynq' or device_type == 'u50' or device_type == 'vck5k'):
			print (str(i).replace('\'status', ' \'status'))	
	print ('\n')

	
def check_in_queue(email, device):
	for i in col_device.find({}, {"_id":0, 'device': 1, 'queue_user':1, 'queue_email': 1}):
		if i['device'] == device:
			if i['queue_user'] == 0:
				return('no queue')
			elif i['queue_email'][0] == email:
				return('queue first')
			elif email in i['queue_email']:
				for j in range(len(i['queue_email'])):
					if i['queue_email'][j] == email:
						return('%sst but not first' %(j+1))
			else:
				return('not in queue')
	return('no device')


def pop_from_queue(email, device):
	for i in col_device.find({}, {"_id":0, 'device': 1, 'queue_user':1, 'queue_email': 1}):
		if device == i['device']:
			update_queue_email = i['queue_email']
			update_queue_email.pop(0)	
			col_device.update_one({'device':i['device']},{ '$set':{ 'queue_email':update_queue_email } })	
			col_device.update_one({'device':i['device']},{ '$set':{ 'queue_user':i['queue_user']-1 } })	
			col_device.update_one({'device':i['device']},{ '$set':{ 'queue_timeout':'00:00:00' } })	


def get_timeup(device):
	for i in col_monitord.find({}, {"_id":0, 'device':1, 'timeup':1}):
		if i['device'] == device and not '00:00:00' ==  i['timeup']:
			return(i['timeup'])
	return('00/00/0000 00:00:00')		
	
	
def current_user(email, device):
	for i in col_monitord.find({}, {"_id":0, 'email':1, 'device':1, 'timeup':1}):
		if i['email'] == email and i['device'] == device and not '00:00:00' ==  i['timeup']:
			return(True)
	return(False)		

									
def add_to_queue(email, device):
	can_add_to_queue = False
	queue_status = check_in_queue(email, device)
	for i in col_monitord.find({}, {"_id":0, 'email':1 , 'ssh_passwd':1}):
		if i['email'] == email:
			if device.replace('u50_', '') in i['ssh_passwd']:
				can_add_to_queue = True
				break
	if not can_add_to_queue:
		print('you are invalid %s tenant' %(alias_to_vck5k(device)))
		print('user %s is added to device %s queue unsuccessfully' %(email, alias_to_vck5k(device)))
	elif current_user(email, device):
		print('you are current user, user %s is added to device %s queue unsuccessfully' %(email, alias_to_vck5k(device)))		
	elif queue_status == 'queue first' or 'but not first' in queue_status:
		num_st = queue_status.replace(' but not first', '') if 'but not first' in queue_status else '1st'
		print('user %s is already added to device %s queue and %s in wait queue' %(email, alias_to_vck5k(device), num_st))
		print('please rent after email notification')
	else:
		for i in col_device.find({}, {"_id":0, 'device': 1, 'queue_user':1, 'queue_email': 1}):
			if device == i['device']:
				update_queue_email = i['queue_email']
				update_queue_email.append(email)
				for j in range(len(update_queue_email)):
					if update_queue_email[j] == '':
						try:
							update_queue_email.pop(j)
						except:
							pass
				col_device.update_one({'device':i['device']},{ '$set':{ 'queue_email':update_queue_email } })
				col_device.update_one({'device':i['device']},{ '$set':{ 'queue_user':i['queue_user']+1 } })	
				timeupstr =	get_timeup(device)
				retimeupstr = timeupstr.replace('/', ' ').split()[0] + '/' + timeupstr.replace('/', ' ').split()[1] + ' ' + timeupstr.replace('/', ' ').split()[-1]
				print('user %s is added to device %s queue and %sst in wait queue successfully' %(email, alias_to_vck5k(device), len(update_queue_email)))
				print('current user will timeup at %s, you will receive a email notification while device %s is your turn' %(retimeupstr, alias_to_vck5k(device)))
		 			

def rent_device_with_queue(email, device, job):	
	available = check_device_available(device)
	if 'is available' in available:		
		queue_status = check_in_queue(email, device)		
		print('device %s is available' %(alias_to_vck5k(device)))
		rent = input('do you want to rent this device? (y/n)\n>> ')
		if (rent == 'y' or rent == 'Y') and (queue_status == 'no queue' or queue_status == 'queue first'):
			if queue_status == 'queue first':
					pop_from_queue(email, device)
			try:				
				res_request = requests.post(MonitordRentRequest, json = {'email':email, 'device':device, 'job':job})
				print(res_request.text)				
			except:
				print('contact OnlineFPGA admin to restart monitord service')
		elif (rent == 'y' or rent == 'Y') and 'but not first' in queue_status:
			print('user %s in device %s queue and %s in wait queue, please rent after email notification' \
			      %(email, alias_to_vck5k(device), queue_status.replace(' but not first', '')))
		elif (rent == 'y' or rent == 'Y') and 'not in queue' in queue_status:			
			add_to_queue(email, device)
		elif rent == 'n' or rent == 'N':
			pass
		else:
			print('your input is invalid')
	else:
		print('device %s current status is %s' %(alias_to_vck5k(device), check_device_status(device)))
		add_to_queue(email, device)


def rent_device(email, device, job):	
	available = check_device_available(device)
	if 'is available' in available:
		print('device %s is available' %(alias_to_vck5k(device)))
		rent = input('do you want to rent this device? (y/n)\n>> ')
		if rent == 'y' or rent == 'Y':
			try:
				res_request = requests.post(MonitordRentRequest, json = {'email':email, 'device':device, 'job':job})
				print(res_request.text)
			except:
				print('contact OnlineFPGA admin to restart monitord service')
		elif rent == 'n' or rent == 'N':
			pass
		else:
			print('your input is invalid')
	else:		
		print('device %s current status is %s' %(alias_to_vck5k(device), check_device_status(device)))	
		

def find_available_device(device_type, job):
	if device_type == 'pynq':
		for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1}):
			if 'pynq' in i['device'] and i['status'] == 'available':
				return(i['device'])
	if device_type == 'kv260':
		for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1}):
			if 'kv260' in i['device'] and i['status'] == 'available':
				return(i['device'])			
	if device_type == 'u50':
		for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1, 'user': 1, 'u50_board':1}):
			if 'u50' in i['device'] and job == 'vitis_tool' and i['user'] == 0:
				return(i['device'])
			if 'u50' in i['device'] and job == 'u50_validation' and i['u50_board'] == 1 and i['user'] < U50UserLimit:
				return(i['device'])
		for i in col_device.find({}, {"_id":0, 'device': 1, 'status': 1, 'user': 1, 'u50_board':1}):
			if 'u50' in i['device'] and job == 'vitis_tool' and i['user'] < U50UserLimit:
				return(i['device'])			
	return('no available device')


def check_available_u50_device(device, job):
	for i in col_device.find({}, {"_id":0, 'device': 1, 'user': 1, 'u50_board':1}):
		if device == i['device']:
			if job == 'u50_validation' and i['u50_board'] == 1:
				return('available device')
			if job == 'vitis_tool' and i['user'] < U50UserLimit:
				return('available device')
	return('not available device')
	

def return_device(email, device):
	used = check_device_used(device)	
	if 'is used' in used:
		print('device %s is in used' %(alias_to_vck5k(device)))
		return_confirm = input('do you want to return this device? (y/n)\n>> ')
		if return_confirm == 'y' or return_confirm == 'Y':
			try:
				job = 'u50_validation' if 'u50' in device else 'pynq' if 'pynq' in device else \
				      'kv260' if 'kv260' in device else ''
				res_request = requests.post(MonitordReturnRequest, json = {'email':email, 'device':device, 'job':job})
				print(res_request.text)			
			except:
				print('contact OnlineFPGA admin to restart monitord service')
		elif return_confirm == 'n' or return_confirm == 'N':
			pass
		else:
			print('your input is invalid')
	else:
		print('device %s is no needed to return' %(alias_to_vck5k(device)))
		

def reg_or_login_menu():
	print('\n')
	print('[1] login')
	print('[0] exit OnlineFPGA service')
	print('\n')

		
def service_menu():
	print('\n')		
	print('[1] list all online device boards')
	print('[2] rent a specified device board')
	print('[3] return your rented device board')
	print('[0] exit OnlineFPGA service')
	print('\n')
	

def device_menu():
	print('\n')
	print('[1] pynq')
	print('[2] kv260')	
	print('\n')	
	
		
def rent_menu():
	print('\n')
	print('[1] rent a device board by choice')
	print('[2] rent a device board by assignment')
	print('\n')
	
	
def job_menu():
	print('\n')
	print('[1] vitis tool')
	#print('[2] only u50 validation')
	print('\n')		
	
	
def service(pts_pid):
	service_menu()
	try:
		option = int(input('please enter your option:\n>> '))
	except:
		option = 4
	
	while option != 0:
		if option == 1:
			list_device('')
			
		elif option == 2:
			device_menu()
			try:
				sub_option = int(input('please enter your option:\n>> '))
			except:
				sub_option = 3
			device_type = 'pynq' if sub_option == 1 else 'kv260' if sub_option == 2 else ''			
			if sub_option == 1 or sub_option == 2:				
				rent_menu()
				try:
					subsub_option = int(input('please enter your option:\n>> '))
				except:
					subsub_option = 3
				if subsub_option == 1:
					list_device(device_type)
					try:
						device = input('please enter %s device name which you want to rent:\n>> ' %(device_type))
						exist = check_device_exist(device) if not 'u50' in device and not 'vck5k' in device else ''						
						if 'is existing' in exist:
							job = 'pynq' if 'pynq' in device else 'kv260'
							rent_device(email, device, job)
						else:
							print('device is not existing')						
					except:
						print('your input is invalid')		
				elif subsub_option == 2:					
					available_device = find_available_device(device_type, '')
					if not 'no available' in available_device:
						try:
							rent_device(email, available_device, device_type)
						except:
							print('your input is invalid')	
					else:
						print('no available device, rent later')
				else:
					print('your input is invalid')			
			else:
				print('your input is invalid')
				
		elif option == 3:
			try:
				device = input('please enter device name which you want to return:\n>> ')
				if 'vck5k' in device:
					device = alias_to_u50(device)
				exist = check_device_exist(device)
				if 'is existing' in exist:
					return_device(email, device)
				else:
					print('device is not existing')
			except:
				print('your input is invalid')
				
		else:
			print('your input is invalid')
			
		service_menu()
		try:
			option = int(input('please enter your option:\n>> '))
		except:
			option = 4
		
	os.system('kill -9 ' + pts_pid)
					  

if __name__ == '__main__':
	  pts_pid = str.split(os.popen(FindPTSCommand).read())[-1]	  
	
	  current_time = datetime.now().strftime('%H:%M')
	  try:
	  	if datetime.strptime(current_time, '%H:%M') >= datetime.strptime(ServiceStop, '%H:%M') and \
	  	   datetime.strptime(current_time, '%H:%M') <= datetime.strptime(ServiceStart, '%H:%M'):
	  	   	print('Current Time is %sam during System Maintenance\n' %(current_time))
	  	   	while True:
	  	   		pass		     		
	  except:
	  	os.system('kill -9 ' + pts_pid)
	
	  reg_or_login_menu()
	  try:
	  	option = int(input('please enter your option:\n>> '))
	  except:
	  	option = 2	  		  
	  	
	  while option != 0:
	  	if option == 1:
	  		
	  		try:
	  			email = input('please enter your register email:\n>> ')
	  			email_invalid = check_email_invalid(email)
	  			if email_invalid:
	  				print(email_invalid)
	  			else:
	  				password = input('please enter your password:\n>> ')
	  				email_passwd = check_email_passwd(email, password)
	  				if 'authentication pass' in email_passwd:
	  					service(pts_pid)
	  				else:
	  					print(email_passwd)
	  		except:
	  			print('your input is invalid')		
	  		
	  	else:
	  		print('your input is invalid')						  	
	  		
	  	reg_or_login_menu()
	  	try:
	  		option = int(input('please enter your option:\n>> '))
	  	except:
	  		option = 2	  		  		  		  	  
	  	
	  os.system('kill -9 ' + pts_pid)