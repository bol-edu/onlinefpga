from notebook.auth import passwd
import json
import time
import os, sys
import random
import string


RemoveExcept = ['Welcome to Pynq.ipynb', '.pynq-notebooks', 'base', 'common', 'kv260', 'pynq-dpu', \
                'pynq-helloworld', 'getting_started', 'logictools', 'pynq_composable', 'pynq_peripherals'] 
pynq_version = 'unknown' 
try:
	pynq_version = '2.7' if '2.7.0' in str.split(os.popen('/usr/local/share/pynq-venv/bin/pynq -v').read()) else 'unknown'
except:
	pass	
	                
                                                       
def get_random_passwd(length):
	  # random string of lower case and upper case letters
    passwd_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return(passwd_str)


def gen_hashedpasswd(password):
    hashedpasswd = passwd(password)
    print ('generate hashed passwd, %s' %(hashedpasswd))    
    dic = {
        "NotebookApp": {
        "password": hashedpasswd
        }
    }    
    json_object = json.dumps(dic, indent = 2)
    with open("jupyter_notebook_config.json", "w") as outfile:
        outfile.write(json_object)
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('need provide passwd and device type for reset pynq')
        sys.exit()
    else:
    	password = sys.argv[1]    	
    	if sys.argv[1] == 'random':
    		password = get_random_passwd(6)
    	print ('set jupyter-notebook web passwd %s in %s' %(password, os.environ['HOME']))
    	
    	if pynq_version == '2.7':
    		gen_hashedpasswd(password)    	
    	else:
    		print('unknown pynq version')
    		sys.exit()

    board = sys.argv[2]
    RemoveList = []
    PynqCmdList = []
    if board == 'pynq':    	
    	RemoveList = os.listdir('/home/xilinx/jupyter_notebooks/')
    	PynqCmdList = ['echo xilinx | sudo -S pkill -f jupyter-notebook', \
    	               'echo xilinx | sudo -S mv ./jupyter_notebook_config.json /root/.jupyter/', \
    	               'echo xilinx | sudo -S /bin/bash /usr/local/bin/start_jupyter.sh']
    if board == 'kv260':
    	RemoveList = os.listdir('/home/root/jupyter_notebooks/')
    	PynqCmdList = ['echo boledukv260 | sudo -S pkill -f jupyter-notebook', \
    	               'echo boledukv260 | sudo -S mv ./jupyter_notebook_config.json /root/.jupyter/', \
    	               'echo boledukv260 | sudo -S /bin/bash /usr/local/bin/start_jupyter.sh']
    	
    for i in RemoveList:
    	if not i in RemoveExcept or 'Untitled Folder' in i:
    		if board == 'pynq':
    			os.system('echo xilinx | sudo -S rm -rf /home/xilinx/jupyter_notebooks/' + '\'' + i + '\'')
    		if board == 'kv260':
    			os.system('echo boledukv260 | sudo -S rm -rf /home/root/jupyter_notebooks/' + '\'' + i + '\'')
    		time.sleep(1)
    
    for i in PynqCmdList:
    	os.system(i)
    	time.sleep(2)

