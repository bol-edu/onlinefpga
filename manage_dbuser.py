import os, sys
from pymongo import MongoClient
from datetime import datetime
import random
import string
import smtplib
from email_validator import validate_email, EmailNotValidError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import *

client = MongoClient(MongoIP, MongoPort)
db = client.boledudb
col_user = db.boleduuser


def get_random_passwd(length):
	  # random string of lower case and upper case letters
    passwd_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return(passwd_str)


def check_email_invalid(email):
	try: 
		email = validate_email(email).email
	except EmailNotValidError as e:
		return(str(e))
		
		
def send_reg_to_email(receiver, name, password):
	msg = MIMEMultipart()
	message = 'user email: ' + receiver + '\n' + 'user name: ' + name + '\n' + 'user passwd: ' + password + '\n' + \
	          'manual link: ' + OnlineFPGAUserManual
	msg['From'] = GmailSender
	msg['To'] = receiver
	msg['Subject'] = 'OnlineFPGA registration' + ' - ' + receiver 
	msg.attach(MIMEText(message, 'plain'))
	text = msg.as_string()
	try:
		smtpserver = smtplib.SMTP(SmtpServer, SmtpPort)
		smtpserver.starttls()
		smtpserver.login(GmailSender, GmailPasswd)
		smtpserver.sendmail(GmailSender, receiver, text)
		smtpserver.close()
		return('send registration is successfully')
	except:
		return('send registration is failed')


def add_dbuser_by_csv(filename):
	csv = open(filename, 'r')
	lines = csv.readlines()
	for i in lines:
		email = i.strip()
		if not email == '':
			add_dbuser(email, '@', '@')
		else:
			print('Skip empty email')	 
	
	
def add_dbuser(email, username, password):
	email_invalid = check_email_invalid(email)
	if email_invalid:
		print(email_invalid)
		print('Generate registration info to %s failed' %(email))
		return('except')
	for i in col_user.find():
		if i['email'] == email:
			print('Email: %s is exist' %(email))
			return('except')
	date_str = datetime.now().strftime('%Y/%m/%d')
	username = email.split('@')[0] if username == '@' else username
	password = get_random_passwd(PasswdLength) if password == '@' else password	
	send_email_result = send_reg_to_email(email, username, password)
	if not 'failed' in send_email_result:
		res = col_user.insert_one({'email':email,'name':username,'password':password,'date':date_str})
		print('User: %s, Email: %s, Passwd: %s, Date: %s is added to DB' %(username, email, password, date_str))
		print('Send registration info to %s successfully' %(email))
	else:
		print('Send registration info to %s failed' %(email))


def del_dbuser(email):
	for i in col_user.find():
		if i['email'] == email:
			col_user.delete_one({'email':email})
			print('Email: %s is removed from DB' %(email))
			return('del specified user')
	print('User %s not found in DB' %(email))
	


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Usage:')
		print('python3 manage_dbuser.py add registration.csv')
		print('python3 manage_dbuser.py add email username password')
		print('python3 manage_dbuser.py del email')
		print('\n')
		sys.exit()
	operation = sys.argv[1]
	if not (operation == 'add' or operation == 'del'):
		print('invalid argument')
		sys.exit()
	if operation == 'add':
		if len(sys.argv) == 3 and os.path.exists(sys.argv[2]):
			add_dbuser_by_csv(sys.argv[2])
		elif len(sys.argv) < 5:
			print('invalid email username password')
			sys.exit()
		else:
			operation == 'add'
			add_dbuser(sys.argv[2], sys.argv[3], sys.argv[4])
	if operation == 'del':
		if len(sys.argv) < 3:
			print('invalid email')
			sys.exit()
		else:
			operation == 'del'
			del_dbuser(sys.argv[2])		
