#! /usr/bin/python

from __future__ import absolute_import, division, print_function
from builtins import *

import sys, os
import json
from colorama import Fore, Back, Style
from multiprocessing.managers import BaseManager
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import threading

import signal
import time

def loadConfig(fileName):
    try:
        with open(fileName,'r') as d:
            jsn = json.load(d)
            jsn['PUBLIC_HTML'] = os.path.normpath(jsn['PUBLIC_HTML'])   # Normalize path
            jsn['ERROR_DIR'] = os.path.normpath(jsn['ERROR_DIR'])   # Normalize path
            jsn['OTHER_TEMPLATES'] = os.path.normpath(jsn['OTHER_TEMPLATES'])   # Normalize path
            return jsn
    except IOError:
        print("Error: File does not appear to exist.")
        sys.exit(1)
    except ValueError:
        print("Error: Config file format not correct.")
        sys.exit(1)
    except:
        print("Error: Something went wrong trying to load the settings.")
        sys.exit(1)

 
    
def log(msg, log_level="INFO"):
    ## Higher is the log_level in the log() argument, the lower is its priority.  

    def getColor(level):
        colors = {
            "WARNING": Fore.LIGHTWHITE_EX+Back.YELLOW,
            "SUCCESS": Fore.LIGHTGREEN_EX,
            "FAIL": Fore.RED,
            "RESET": Style.RESET_ALL,
            "INFO": Fore.BLUE,
        }
        return colors[log_level] if level in colors else Fore.BLUE

    print("[{}] >> {}{}{} <".format(log_level, getColor(log_level), repr(msg), Style.RESET_ALL))

def preventExit():
    original_sigint = signal.getsignal(signal.SIGINT)
    # restore the original signal handler as otherwise evil things will happen
    def exit_gracefully(signum, frame):
        import sys
        signal.signal(signal.SIGINT, original_sigint)
        sys.exit(1)

    signal.signal(signal.SIGINT, exit_gracefully)


class Manager:
    def get_distance_time(self):
        print('started by thread %s'%(threading.get_ident()))
        # assume that network request was made here
        time.sleep(1)
        print('ended by thread %s'%(threading.get_ident()))
    def send_message(self, message):
        formatted_message = '{} >> {}'.format( time.ctime(time.time()), message )
        print(formatted_message)
        
def server():
    

    _api=Manager()
    BaseManager.register('API', lambda: _api)
    manager = BaseManager(address=('localhost', 5000), authkey=b'')
    server = manager.get_server()
    server.serve_forever()

def client():
    manager = BaseManager(address=('localhost', 5000), authkey=b'')
    manager.connect()
    executor = ThreadPoolExecutor(max_workers=3)
    # client mades three simultaneous requests to the server
    _api = manager.API()
    _api.send_message('♫')
    a = executor.submit(_api.get_distance_time)
    print('♫')
    while True:
         cmd =  input('> ')
         _api.send_message( cmd )

if __name__ == '__main__':
    log('chuj')