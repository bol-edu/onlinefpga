from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from config import *
import sys
import time
import requests


def fpga_init():
	fpga_no_init = True
	while fpga_no_init:
		try:
			resp = requests.post(MonitordInitRequest)
			fpga_no_init = False
		except:
			print('wait monitord service..')
			time.sleep(1)
												
	print('http fpga_init request to monitord %s:%s at %s successfully' \
	      %(MonitordIP, MonitordPort, datetime.now().strftime('%H:%M:%S')))
	return(resp)
	
def retry_unknown():
	fpga_no_retry_unknown = True
	while fpga_no_retry_unknown:
		try:
			resp = requests.post(MonitordRetryUnknownRequest)
			fpga_no_retry_unknown = False
		except:
			print('wait monitord service..')
			time.sleep(1)
		
	print('http retry_unknown request to monitord %s:%s at %s successfully' \
	      %(MonitordIP, MonitordPort, datetime.now().strftime('%H:%M:%S')))
	return(resp)


def retry_available(device):
	fpga_no_retry_available = True
	while fpga_no_retry_available:
		try:
			resp = requests.post(MonitordRetryAvailRequest, json = {'device':device})
			fpga_no_retry_available = False
		except:
			print('wait monitord service..')
			time.sleep(1)
		
	print('http retry_available request to monitord %s:%s at %s successfully' \
	      %(MonitordIP, MonitordPort, datetime.now().strftime('%H:%M:%S')))
	return(resp)

	
def check_and_action():
	fpga_no_check = True
	while fpga_no_check:
		try:
			resp = requests.post(MonitordCheckRequest)
			fpga_no_check = False
		except:
			print('wait monitord service..')
			time.sleep(1)
		
	print('http check_and_action request to monitord %s:%s at %s successfully' \
	      %(MonitordIP, MonitordPort, datetime.now().strftime('%H:%M:%S')))
	

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('\n')
		print('Usage:')
		print('python3 active_monitord.py fpga_init')
		print('python3 active_monitord.py retry_unknown')
		print('python3 active_monitord.py retry_available device')
		print('python3 active_monitord.py run_routine')
		print('python3 active_monitord.py run_startup')
		print('\n')
		sys.exit()
	
	job = sys.argv[1]	
	scheduler = BlockingScheduler()
	if job == 'fpga_init':
		resp = fpga_init()
	elif job == 'retry_unknown':
		resp = retry_unknown()
	elif job == 'retry_available':
		try:
			device = sys.argv[2]
		except:
			print('Invalid device')	
			sys.exit()
		resp = retry_available(device)	
	elif job == 'run_routine':
		scheduler.add_job(check_and_action, 'interval', seconds=CheckSeconds)
		scheduler.add_job(retry_unknown, 'interval', minutes=RetryMinutes)		
		scheduler.start()
	elif job == 'run_startup':
		resp = fpga_init()
		scheduler.add_job(check_and_action, 'interval', seconds=CheckSeconds)
		scheduler.add_job(retry_unknown, 'interval', minutes=RetryMinutes)
		scheduler.start()
	else:
		pass