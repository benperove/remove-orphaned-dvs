#!/usr/bin/env python

'''
Remove Orphaned N1K DVS - benperove@gmail.com
'''

import re
import os
import sys
import string
import subprocess

#USER variables - modify accordingly
vsm_ip               = '10.21.16.39'
vc_ip                = '10.21.16.42'
vc_dc_name           = 'Datacenter'
vc_extension_key     = 'Cisco_Nexus_1000V_792243929'
vc_orphaned_dvs_name = 'switch'

#SYSTEM variables - do not modify!!
rsa_key              = '/etc/ssh/ssh_host_rsa_key'
vsm_user             = 'tempuser'
base_cmd             = 'ssh -oStrictHostKeyChecking=no -i '+rsa_key+' '+vsm_user+'@'+vsm_ip+' '

def run(cmd, ignore_code=0):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	retcode = p.wait()
	if retcode != 0 and retcode != ignore_code:
		return retcode
	else:
		return out

def vsm_command(cmd):
	result = run(base_cmd+cmd)
	return result

def check_vsm_connection():
	cmd = base_cmd+'sh ver'
	test = run(cmd)
	if re.search('kickstart', test):
		print 'Connecting to VSM ... OK.'
		return True
	else:
		print 'Connecting to VSM ... failed.'
		return False
		sys.exit

def check_svs_conn():
	result = vsm_command('sh svs connection')
	for line in result.splitlines():
		if re.search(':', line):
			items = line.strip().split(':')
			if items[0] == 'operational status':
				if items[1].strip() == 'Connected':
					print 'VSM is connected to VC.'
					return True
				else:
					print 'VSM is not connected to VC.'
					return False

def get_vc_extension_key():
	result = vsm_command('sh vmware vc ext')
	for line in result.splitlines():
		if re.search(':', line):
			items = line.strip().split(':')
			if items[0] == 'Extension ID':
				return items[1].strip()
			else:
				return 'could not verify extension key'

def conf_vc_extension_key(key):
	current_key = get_vc_extension_key()
	print 'Current VC extension-key: '+current_key
	if current_key != key:
		vsm_command('\'echo "conf t" >> bootflash:script.cfg\'')
		vsm_command('\'echo "vmware vc extension-key '+key+'" >> bootflash:script.cfg\'')
		vsm_command('\'run-script bootflash:script.cfg\'')
		vsm_command('\'del bootflash:script.cfg\'')
		print 'New VC extension-key: '+get_vc_extension_key()
	else:
		print 'No changes to VC extension-key required.'

def conf_vsm_switchname(vc_orphaned_dvs_name):
	result = vsm_command('sh switchname')
	if result.strip() != vc_orphaned_dvs_name:
		vsm_command('\'echo "conf t" >> bootflash:script.cfg\'')
		vsm_command('\'echo "switchname '+vc_orphaned_dvs_name+'" >> bootflash:script.cfg\'')
		vsm_command('\'run-script bootflash:script.cfg\'')
		vsm_command('\'del bootflash:script.cfg\'')
		switchname = vsm_command('sh switchname')
		print 'Switchname changed to: '+switchname.strip()
	else:
		print 'Keeping existing switchname.'

def conf_svs_conn():
	vsm_command('\'echo "conf t" >> bootflash:script.cfg\'')
	vsm_command('\'echo "svs conn vc" >> bootflash:script.cfg\'')
	vsm_command('\'echo "no connect" >> bootflash:script.cfg\'')
	vsm_command('\'echo "protocol vmware-vim" >> bootflash:script.cfg\'')
	vsm_command('\'echo "vmware dvs datacenter-name '+vc_dc_name+'" >> bootflash:script.cfg\'')
	vsm_command('\'echo "remote ip address '+vc_ip+'" >> bootflash:script.cfg\'')
	vsm_command('\'echo "connect" >> bootflash:script.cfg\'')
	result = vsm_command('\'run-script bootflash:script.cfg\'')
	vsm_command('\'del bootflash:script.cfg\'')
	if re.search('ERROR', result):
		print 'It appears that extension-key '+vc_extension_key+' was not properly registered. Use -k first.'
		sys.exit()
	else:
		print 'VC extension-key '+vc_extension_key+' appears to be valid.'

def conf_remove_dvs():
	vsm_command('\'echo "conf t" >> bootflash:script.cfg\'')
	vsm_command('\'echo "svs conn vc" >> bootflash:script.cfg\'')
	vsm_command('\'echo "no vmware dvs" >> bootflash:script.cfg\'')
	vsm_command('\'echo "yes" >> bootflash:script.cfg\'')
	vsm_command('\'run-script bootflash:script.cfg\'')
	vsm_command('\'del bootflash:script.cfg\'')
	result = vsm_command('sh svs connection')
	for line in result.splitlines():
		if re.search(':', line):
			items = line.strip().split(':')
			if items[0] == 'datacenter name':
				if items[1].strip() == '-':
					print 'OK.'
					print "Don't forget to remove the old extension key in the VC MOB."
					return True
				else:
					print 'FAILED. Check error messages in VC.'
					return False

def ping_vc():
	result = vsm_command('\'ping '+vc_ip+' vrf management\'')
	if re.search('icmp_seq=[0-9]+', result.strip()):
		print 'Ping to VC successful.'
	else:
		print 'Ping to VC failed.'
		sys.exit()

def print_help(unknown_option=None):
	options = \
	{
		'-h | --help': 'Print help',
		'-d | --delete': 'Delete orphaned DVS (make sure to run -k first!)',
		'-k | --key': 'Change VSM extension key to match extension key of the orphaned DVS'
	}
	os.system('clear')
	if unknown_option:
		print unknown_option+'\n'
	print "Usage: remove-orphaned-dvs.py [options]\n"
	print "OPTIONS:\n"
	for option in options:
		print "{0:20} {1:50}".format(option, options[option])
	print "\r"

def main():
	try:
		if len(sys.argv) > 1:
			if (sys.argv[1] == '-k') | (sys.argv[1] == '--key'):
				os.system('clear')
				check_vsm_connection()
				print 'Switchname: '+vsm_command('sh switchname').strip()
				check_svs_conn()
				conf_vc_extension_key(vc_extension_key)
				print 'Download new extension key (http://vsm_ip_address), save cisco_nexus_1000v_extension.xml, add plug-in to VC, then use -d option.'
				sys.exit()
			elif (sys.argv[1] == '-d') | (sys.argv[1] == '--delete'):
				os.system('clear')
				check_vsm_connection()
				print 'Switchname: '+vsm_command('sh switchname').strip()
				check_svs_conn()
				conf_vc_extension_key(vc_extension_key)
				conf_vsm_switchname(vc_orphaned_dvs_name)
				ping_vc()
				conf_svs_conn()
				if check_svs_conn():
					print 'Removing orphaned DVS ...',
					conf_remove_dvs()
			elif (sys.argv[1] == '-h') | (sys.argv[1] == '--help'):
				print_help()
				sys.exit()
			else:
				unknown_option = 'Unknown option: '+sys.argv[1]
				print_help(unknown_option)
				sys.exit()
		else:
			print_help()
			sys.exit()

	except ImportError, e:
		print "It didn't work."
		print e.args[0]
		sys.exit()

if __name__ == "__main__":
	main()
