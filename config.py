#############################################################################
# mongodb
#############################################################################
MongoIP = '172.17.0.2'
MongoPort = 27017
#############################################################################
# monitord
#############################################################################
MonitordIP = '192.168.1.10'
MonitordPort = 5000
RentedPynqMinutes = 60
RentedKv260Minutes = 120
RentedVitisMinutes = 60
RentedU50Minutes = 120
RentedU50JobMinutes = 100
RentedU50BatchHours = 6
PasswdLength = 6
PynqZ2List = ['01', '02', '03', '04', '05', '06', '07', '09', '10', '11', '12']
Kv260List = ['02', '03', '04', '05', '06', '08', '09', '10', '11', '12', '13', '20']
PynqUserName = 'xilinx'
PynqUserPasswd = 'xilinx'
PynqZ2Home = '/home/xilinx/'
Kv260UserName = 'ubuntu'
Kv260UserPasswd = 'boledukv260'
Kv260Home = '/home/ubuntu/'
PynqPython3 = '/usr/local/share/pynq-venv/bin/python3'
PynqResetFile = 'reset_pynq.py'
U50List = ['01', '02', '03', '04', '05']
U50UserNameList = ['hls01', 'hls02', 'hls03', 'hls04', 'hls05']
# each sudo password must contain its HLS number (01~05)
U50UserPassWordList = ['hls01-passwd', 'hls02-passwd', 'hls03-passwd', 'hls04-passwd', 'hls05-passwd']
U50BoardAvailable = [1, 1, 1, 1, 1]
U50UserLimit = 1
U50BatchLimit = 1
U50Python3 = '/usr/bin/python3'
U50ManageUserHome = '/opt/labManageKit/'
U50ManageUserFile =  'manage_user.py'
U50JobGrabberFile =  'job_grabber.py'
U50DevGroup = 'render'
U50DockerGroup = 'docker'
U50RentedLogFile = '/opt/labManageKit/u50_rented.log'
NcCommand = 'nc -w 5'
ExternalIP = '140.112.207.100'
ExternalIPGateway = '140.112.207.254'
ExternalIPBak = '<external_ip2>'
ExternalIPBakGateway = '<external_gateway2>'
InternalSec = '192.168.1.'
DefaultSSHPort = 22
MonitordInLab = True
U50QueueEnable = True
U50QueueTimeOut = 10
#############################################################################
# onlinefpga
#############################################################################
MonitordRentRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'fpga_rent'
MonitordReturnRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'fpga_return'
VaildCodeLength = 6
SmtpPort = 587
SmtpServer = 'smtp.gmail.com'
GmailSender = '<sender-email>'
GmailPasswd = '<app-password>' 
ServiceStop = '06:00'
ServiceStart = '07:00'
FindPTSCommand = 'ps -ef | grep -E \'ssh.*pts\' | grep -v grep |awk -F\" \" \'{print $2}\''
OnlineFPGAUserManual = 'https://docs.google.com/document/d/1IEI1o_eFKH5lALoFtsIH5fS1nsLZ2yHe/edit?usp=sharing&ouid=106716318998274820333&rtpof=true&sd=true'
#############################################################################
# manage_user
#############################################################################
U50UserHome = '/mnt/HLSNAS/'
TimeCheckFile = './.timeup_check.py'
TimeCheckPycFile = './.timeup_check.pyc'
ChangeDirFile = './.changedir.py'
ChangeDirPycFile = './.changedir.pyc'
#############################################################################
# manage_dbuser
#############################################################################

#############################################################################
# job_grabber
#############################################################################
MonitordJobUpdateRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'batch_jobber'
#############################################################################
# active_monitord
#############################################################################
CheckSeconds = 30
RetryMinutes = 30
MonitordInitRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'fpga_init'
MonitordRetryUnknownRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'retry_unknown'
MonitordRetryAvailRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'retry_available'
MonitordCheckRequest = 'http://' + MonitordIP + ':' + str(MonitordPort) + '/' + 'check_and_action'
