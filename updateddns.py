#!/usr/bin/python
""" 
This is a python script for updating your FreeDNS account. This can be
adapted for other services by changing the first string in the update_url
variable below.

****Make sure you get your update key, and put it between the quotes below in
the update_key variable!!

You can find your FreeDNS update key by logging into your freedns account
online, and then clicking Dynamic DNS in the menu on the left, then at the
bottom of the page, right-click Direct URL and copy the link. Paste the link
below. The KEY is everything after the ?, so delete everything up to and
including the ?. You can see that the update_url variable builds this URL
everytime.

This program creates/uses a file called ".freedns_ip" in the directory of the
script. It also creates various log files.

****Make sure the script has read/write access to this directory!

I have implemented cyclical logging, so when the log is full, it gets moved
to log.1, and log.1 gets shifted to log.2, etc. Each log file is 4096 bytes
and there are 7 log file backups. The default logging level is INFO. You can
change that by changing the [.setlevel(INFO)] to [.setlevel(DEBUG)] below,
under the creating logger section and the creating handler section.

I used WTFismyIP.com to fetch the external IP address. You can substitue for
another if you know what you're doing.

This script is free, and licensed under GPL2. It comes with NO warranties or
guarantees, and I have no liabilities. Enjoy.

****This script is designed to be added to your crontab
([crontab -e] in most distros) and can be run by referencing its location
because I put the shebang at the top. You can, however, manually run it via
python /path/to/script.py

Normally, you can create a folder in your home directory like this:
mkdir ~/.ddns

Then copy this script to that directory. Then add the following to your crontab:
*/5 * * * * /home/user/.ddns/updateddns.py

Just replace "user" with your username.
"""

import sys
import os
from datetime import datetime
from urllib import urlopen
import logging
from logging.handlers import RotatingFileHandler

# Find the PWD, extract the path, and cd to PWD
abspath = os.path.abspath(__file__)
pwd = os.path.dirname(abspath)
os.chdir(pwd)

# Creating logger
logger = logging.getLogger('ddnslogger')
logger.setLevel(logging.INFO)
# Creating handler
fl = logging.handlers.RotatingFileHandler("ddnslog.log", maxBytes = 4096, backupCount = 7)
fl.setLevel(logging.INFO)
# Creating formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s :: %(message)s', '%m-%d-%Y @ %H:%M:%S')
# Adding formatter to handler
fl.setFormatter(formatter)
# Adding handler to logger
logger.addHandler(fl)

# logger's msg variable
msg = ""

# FreeDNS Update Key
update_key = ""

# FreeDNS Update URL
update_url = "http://freedns.afraid.org/dynamic/update.php?" + update_key
 
# External IP URL (must return an IP in plain text)
ip_url = "http://ipv4.wtfismyip.com/text"
 
# Open URL to return the external IP
external_ip = urlopen(ip_url).read()
external_ip = external_ip.rstrip('\n')
last_external_ip = ""
 
# The file where the last known external IP is written
ip_file = ".freedns_ip"

# Check if ip_file exists, if not, create it
if not os.path.exists(ip_file):
        logger.debug("ip_file does not exist, creating it now")
        fi = open(ip_file, "w")
        fi.write(external_ip)
        fi.close()
        last_external_ip = "Unknown"
        logger.debug("ip_file creation: success, value is: " + last_external_ip)
else:
        logger.debug("ip_file exists ( '-')b")
        f = open(ip_file, "r")
        last_external_ip = f.read()
        f.close()
        last_external_ip = last_external_ip.rstrip('\n')
        logger.debug("last external ip is: " + last_external_ip)
logger.info("ip_file verified, last_external_ip set")

# Compare ips and update accordingly
if last_external_ip != external_ip:
	urlopen(update_url)
        msg = "Updating IP from (" + last_external_ip + ") to (" + external_ip + ")"
        print msg
        logger.info(msg)
        f = open(ip_file, "w")
        f.write(external_ip)
        f.close()
        logger.debug("external ip updated")
else:
        last_ip_update = datetime.fromtimestamp(os.path.getmtime(ip_file)).strftime("%m-%d-%Y @ %H:%M:%S")
        msg = "External IP (" + external_ip + ") has not changed. Last update was: " + last_ip_update
        print msg
        logger.info(msg)
        logger.debug("external ip is the same as from " + last_ip_update)
if datetime.now().strftime("%d") != datetime.fromtimestamp(os.path.getmtime(ip_file)).strftime("%d"):
	msg = "IP not updated in 24 hours, updated anyway"
	urlopen(update_url)
	f = open(ip_file, "w")
	f.write(external_ip)
	f.close()
	print msg
	logger.info(msg)
logger.debug("end of script")
