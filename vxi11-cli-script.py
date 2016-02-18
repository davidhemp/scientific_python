#!C:\Python27\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'python-vxi11==0.7','console_scripts','vxi11-cli'
__requires__ = 'python-vxi11==0.7'
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.exit(
        load_entry_point('python-vxi11==0.7', 'console_scripts', 'vxi11-cli')()
    )
