#!/usr/bin/python3
import sys
import time
import logging

import pychromecast
import pychromecast.controllers.dashcast_fork as dashcast


def main(chromecast_ip, server_ip, debug):
    print(server_ip)
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        
    cast = None

    try: 
        cast = pychromecast.Chromecast(chromecast_ip)
    except:
        print('Failed to find chromecast @ ', chromecast_ip) 
        sys.exit(1)
     
    if cast is None:
        print(chromecast_ip, 'not found') 
        sys.exit(1)

    pychromecast.IGNORE_CEC.append('*')
    
    cast.wait()
    d = dashcast.DashCastForkController()
    cast.register_handler(d)


    print(cast.device)
    print(cast.status)
    print(cast.media_controller.status)
    time.sleep(1)

    if not cast.is_idle:
        print
        print("Killing current running app")
        cast.quit_app()
        time.sleep(5)
    

    time.sleep(1)
    
    url = 'http://' + server_ip + '/tv/instructions.php'
    print(url)
    d.load_url(url, True)
    
    if debug:
        time.sleep(2)
    
    if cast.is_idle:
        print('Failed to cast pairing instructions page')
        sys.exit(1)
    sys.exit(0)

if __name__== '__main__':
    if len(sys.argv) < 3:
        print('Usage:  call with Chromecast IP and server IP')
        sys.exit(1)
    print(sys.argv[1])
    server_ip = sys.argv[2]
    debug = True
    #if (len(sys.argv) == 3) and sys.argv[2] == 'd':
    #    debug = True
    main(sys.argv[1], server_ip, debug)
