#!/bin/bash
[ -f /home/boleduuser/onlinefpga.pyc ] && echo hls00-passwd | sudo -S chattr -i /home/boleduuser/onlinefpga.pyc
echo hls00-passwd | sudo -S cp -f __pycache__/onlinefpga.cpython-38.pyc /home/boleduuser/onlinefpga.pyc
echo hls00-passwd | sudo -S chattr +i /home/boleduuser/onlinefpga.pyc

[ -f /home/boleduuser/config.pyc ] && echo hls00-passwd | sudo -S chattr -i /home/boleduuser/config.pyc
echo hls00-passwd | sudo -S cp -f __pycache__/config.cpython-38.pyc /home/boleduuser/config.pyc
echo hls00-passwd | sudo -S chattr +i /home/boleduuser/config.pyc
echo "synchronize config.pyc onlinefpga.pyc to OnlineFPGA boleduuser"
