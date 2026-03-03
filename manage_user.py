import os, sys, time
import crypt
import random
import string
import py_compile
from datetime import datetime
from datetime import timedelta
import subprocess
from config import *


def get_device_passwd():
	hostname = os.popen('hostname').read().rstrip('\n')
	device_id = hostname.replace('HLS', '')
	for i in range(len(U50UserPassWordList)):
		if device_id in U50UserPassWordList[i]:
			passwd = U50UserPassWordList[i]
	return(device_id, passwd)
	  
  
def create_changedir_file(ChangeDirFile, username):
	fout = open(ChangeDirFile, "wt")
	fout.write('import os, sys\n\n')
	fout.write('exclusive_list = [\'\\\\\', \'/\']\n')	
	fout.write('path_root = \'' + U50UserHome + username + '\'\n\n')
	fout.write('try:\n')
	fout.write('    path_var = sys.argv[1]\n')
	fout.write('except:\n')
	fout.write('   sys.exit()\n\n')
	fout.write('path_current = os.getcwd()\n')
	fout.write('if path_var == \'~\':\n')
	fout.write('    path_change = path_root\n')
	fout.write('elif path_var[0] == \'/\':\n')
	fout.write('    path_change = path_var\n')
	fout.write('else:\n')
	fout.write('    path_change = path_current + \'/\' + path_var.rstrip(\'/\')\n\n')
	fout.write('if path_var in exclusive_list or path_change == path_root + \'/\' + \'..\' or not path_root in path_change:\n')
	fout.write('    pass\n')
	fout.write('else:\n')
	fout.write('    os.system(\'echo %s > %s\' %(\'pushd \' + path_change, \'~/.changedir.sh\'))\n')
	fout.write('    os.system(\'echo %s >> %s\' %(\'$SHELL\', \'~/.changedir.sh\'))\n')
	fout.write('    os.system(\'sh %s\' %(\'~/.changedir.sh\'))\n')
	fout.close()

def create_time_check_file(timeupstr, TimeCheckFile, username):
	fout = open(TimeCheckFile, "wt")
	fout.write('import os\n')
	fout.write('import time\n')
	fout.write('from datetime import datetime\n\n')
	timeupstr = 'timeupstr = ' + '\'' + timeupstr.replace('_', ' ') + '\''
	username = 'username = ' + '\'' + username + '\''
	fout.write(timeupstr + '\n')
	fout.write(username + '\n\n')
	fout.write('while True:\n')
	fout.write('    if datetime.now() > datetime.strptime(timeupstr, \'%m/%d/%Y %H:%M:%S\'):\n')
	fout.write('        os.system(\'killall -w -u \' + username)\n')
	fout.write('    else:\n')
	fout.write('        time.sleep(5)')
	fout.close()


def add_user(username, job, timeupstr):
	password = username
	encrypted_password = crypt.crypt(password, username)
	device_id, hls_passwd = get_device_passwd()
	try:
		if not os.path.exists(U50UserHome + username):
			os.system('echo %s | sudo -S useradd -m %s -p %s --home %s%s' %(hls_passwd, username, encrypted_password, U50UserHome, username))
			if job == 'u50_validation':
				os.system('echo %s | sudo -S usermod -a -G %s %s' %(hls_passwd, U50DevGroup, username))
				os.system('echo %s | sudo -S usermod -a -G %s %s' %(hls_passwd, U50DockerGroup, username))
			create_time_check_file(timeupstr, TimeCheckFile, username)
			py_compile.compile(TimeCheckFile, TimeCheckPycFile)
			os.system('echo %s | sudo -S cp -f %s %s%s/%s' %(hls_passwd, TimeCheckPycFile, U50UserHome, username, TimeCheckPycFile))
			time.sleep(1.5)
			os.system('echo %s | sudo -S sed -i \'1i python3 %s &\' %s%s/.bashrc' %(hls_passwd, TimeCheckPycFile.replace('./', '~/'), U50UserHome, username))			
			create_changedir_file(ChangeDirFile, username)
			py_compile.compile(ChangeDirFile, ChangeDirPycFile)
			os.system('echo %s | sudo -S cp -f %s %s%s/%s' %(hls_passwd, ChangeDirPycFile, U50UserHome, username, ChangeDirPycFile))
			time.sleep(1.5)
			cd_alias = 'alias cd=\\\'python3 ' + ChangeDirPycFile + '\\\''
			cd_alias = cd_alias.replace('./', '\~/')
			os.system('echo %s | sudo -S echo %s >> %s%s/.bashrc' %(hls_passwd, cd_alias, U50UserHome, username))			
			os.system('echo %s | sudo -S chown root:%s %s%s' %(hls_passwd, username, U50UserHome, username))
			os.system('echo %s | sudo -S chmod 1775 %s%s' %(hls_passwd, U50UserHome, username))
			os.system('echo %s | sudo -S chown root %s%s/.bashrc' %(hls_passwd, U50UserHome, username))
			os.system('echo %s | sudo -S chown root %s%s/%s' %(hls_passwd, U50UserHome, username, TimeCheckPycFile))
			os.system('echo %s | sudo -S chown root %s%s/%s' %(hls_passwd, U50UserHome, username, ChangeDirPycFile))
			print("create %s user %s and connection end at %s " %('u50_' + device_id, username, timeupstr))
			os.system('echo %s | sudo -S rm -f %s %s %s %s' %(hls_passwd, TimeCheckFile, TimeCheckPycFile, ChangeDirFile, ChangeDirPycFile))
		else:
			create_time_check_file(timeupstr, TimeCheckFile, username)
			py_compile.compile(TimeCheckFile, TimeCheckPycFile)
			os.system('echo %s | sudo -S cp -f %s %s%s/%s' %(hls_passwd, TimeCheckPycFile, U50UserHome, username, TimeCheckPycFile))			
			time.sleep(1.5)
			os.system('echo %s | sudo -S chown root %s%s/%s' %(hls_passwd, U50UserHome, username, TimeCheckPycFile))
			os.system('echo %s | sudo -S rm -f %s %s %s %s' %(hls_passwd, TimeCheckFile, TimeCheckPycFile, ChangeDirFile, ChangeDirPycFile))
			if job == 'u50_validation':
				os.system('echo %s | sudo -S usermod -a -G %s %s' %(hls_passwd, U50DevGroup, username))	
			if job == 'u50_batch':
				os.system('echo %s | sudo -S gpasswd -d %s %s' %(hls_passwd, username, U50DevGroup))		
	except Exception as e:
		print('failed to add user')
		print(e)
		sys.exit()


def del_user(username, job, timeupstr):
	device_id, hls_passwd = get_device_passwd()
	try:		
		timeupstr = datetime.now().strftime('%m/%d/%Y %H:%M:%S')		
		create_time_check_file(timeupstr, TimeCheckFile, username)
		py_compile.compile(TimeCheckFile, TimeCheckPycFile)
		os.system('echo %s | sudo -S cp -f %s %s%s/%s' %(hls_passwd, TimeCheckPycFile, U50UserHome, username, TimeCheckPycFile))
		time.sleep(1.5)
		os.system('echo %s | sudo -S chown root %s%s/%s' %(hls_passwd, username, U50UserHome, TimeCheckPycFile))
		os.system('echo %s | sudo -S rm -f %s %s %s %s' %(hls_passwd, TimeCheckFile, TimeCheckPycFile, ChangeDirFile, ChangeDirPycFile))
		os.system('echo %s | sudo -S killall -w -u %s' %(hls_passwd, username))
		#os.system('echo %s | sudo -S userdel %s' %(hls_passwd, username))
		#os.system('echo %s | sudo -S rm -rf %s%s' %(hls_passwd, U50UserHome, username))
	except:
		print('failed to delete user')
		sys.exit()


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Usage:')
		print('python3 manage_user.py add username job timeupstr')
		print('python3 manage_user.py del username job timeupstr')
		print('\n')
		sys.exit()
	operation = sys.argv[1]
	if operation == 'add' or operation == 'del':
		if len(sys.argv) < 5:
			print('no username, no job and no timeupstr')
			sys.exit()
		else:
			if operation == 'add':
				add_user(sys.argv[2], sys.argv[3], sys.argv[4])
			else:
				del_user(sys.argv[2], sys.argv[3], sys.argv[4])
	else:
		print('invalid argument')
		sys.exit()
