#!/usr/bin/python3
import sys
import argparse
import time
import logging
import signal

import pychromecast
import pychromecast.controllers.dashcast_fork as dashcast
from pychromecast.config import APP_DASHCAST_FORK

has_timed_out = False
cast = None

def response_timeout(signum, frame):
    global cast
    try:
        cast.quit_app()
    except:
        pass
    raise Exception("Waited more 5 seconds for a response from instructions page")

def main(chromecast_ip, url, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        
    global cast
    global has_timed_out

    try: 
        cast = pychromecast.Chromecast(chromecast_ip)
    except:
        print('Failed to find chromecast @ ', chromecast_ip) 
        sys.exit(1)
     
    if cast is None:
        print(chromecast_ip, 'not found') 
        sys.exit(1)

    pychromecast.IGNORE_CEC.append('*')
    
    timeout = 5
    # If cast.wait times out it will return False
    has_timed_out = not cast.wait(timeout)

    d = dashcast.DashCastForkController()
    cast.register_handler(d)

    #print(cast.device)
    #print(cast.status)
    #print(cast.media_controller.status)

    #time.sleep(1)

    if not cast.is_idle:
        print("Killing current running app")
        cast.quit_app()
        time.sleep(5)
    
    #time.sleep(1)

    casting_instructions = False
    if (url.endswith('instructions.php')):
        casting_instructions = True

    d.load_url(url, not casting_instructions)

    # Need to wait 2 seconds after url is loaded before testing if idle
    time.sleep(2.5)

    if casting_instructions:
        signal.signal(signal.SIGALRM, response_timeout)
        signal.alarm(5)
        while cast.status.status_text != 'Successfully loaded page!':
            time.sleep(1)
    
    if cast.is_idle:
        print('Failed to cast url')
        cast.quit_app()
        sys.exit(1)
    elif cast.app_id != APP_DASHCAST_FORK:
        print(cast.app_display_name, cast.app_id)
        sys.exit(1)
    sys.exit(0)

if __name__== '__main__':
    parser = argparse.ArgumentParser(description='Cast a URL to a chromecast device')
    parser.add_argument('--deviceip', required=True)
    parser.add_argument('--url', required=True)
    parser.add_argument('-d', '--debug', action='store_const', const=True)
    args = vars(parser.parse_args())

    try:
        main(args['deviceip'], args['url'], args['debug'])
    except Exception as e:
        print('Exiting because of exception: %s' % e)
        if has_timed_out:
            print('cast.wait() timeout')
            sys.exit(2)
        sys.exit(1)
