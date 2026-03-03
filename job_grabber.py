import os, sys
import os.path
import time
import requests
import subprocess
from config import *


def get_device_passwd():
    hostname = os.popen('hostname').read().rstrip('\n')
    device_id = hostname.replace('HLS', '')
    for i in range(len(U50UserPassWordList)):
        if device_id in U50UserPassWordList[i]:
            passwd = U50UserPassWordList[i]
    return(device_id, passwd)
            

def update_to_monitord(email, job_list, job_pid, status):
	no_job_status_return = True
	while no_job_status_return:
		try:
			requests.post(MonitordJobUpdateRequest, json = {'jobber':'update', 'email':email, 'job_list':job_list, 'job_pid':'', 'status':status})
			no_job_status_return = False
		except:
			time.sleep(30)


def monitor_job(email, job_path):	
	device_id, hls_passwd = get_device_passwd()
	grep_cmd = 'ps -ef | grep -E \'echo ' + hls_passwd + ' |sudo -S make all -C ' + \
	           job_path + '\' | grep -v grep |awk -F\" \" \'{print $2}\''
	while True:
		try:
			job_id = int(str.split(os.popen(grep_cmd).read())[0])
			if job_id > 0:
				requests.post(MonitordJobUpdateRequest, json = {'jobber':'update', 'email':email, 'job_list':[job_path], 'job_pid':str(job_id), 'status':'run'})
				time.sleep(30)
		except:
			break	


def kill_job(email, job_path):
	device_id, hls_passwd = get_device_passwd()
	kill_cmd = 'echo' + ' ' + hls_passwd + ' ' + '|sudo -S pkill -f' + ' ' + job_path
	proc_kill = subprocess.Popen(kill_cmd, shell=True)	
	
	
def run_job(email, job_path):
	device_id, hls_passwd = get_device_passwd()
	clean_cmd = 'echo' + ' ' + hls_passwd + ' ' + '|sudo -S make clean -C' + ' ' + job_path
	make_cmd = 'echo' + ' ' + hls_passwd + ' ' + '|sudo -S make all -C' + ' ' + job_path
	os.system(clean_cmd)
	time.sleep(2)	
	os.system(make_cmd)
	#monitor_job(email, job_path)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:')
        print('python3 job_grabber.py run email job_path')
        print('python3 job_grabber.py kill email job_path')
        print('\n')
        sys.exit()
        
    job = sys.argv[1]
    email = ''
    job_path = ''
    if job == 'run' or job == 'kill':
    	try:
    		email = sys.argv[2]
    		job_path = sys.argv[3]
    	except:
    		print('Invalid argument')
    		sys.exit()
    else:
    	print('Invalid option')	
    	sys.exit()
    	
    if not os.path.exists(job_path + 'makefile'): 
    	update_to_monitord(email, [job_path], '', 'error')
    	sys.exit()
    	
    if job == 'run':
    	update_to_monitord(email, [job_path], '', 'run')
    	run_job(email, job_path)    	
    	update_to_monitord(email, [job_path], '', 'finish')    
    			
    if job == 'kill':
    	kill_job(email, job_path)
    	update_to_monitord(email, [job_path], '', 'kill')