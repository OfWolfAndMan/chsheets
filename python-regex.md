### Separate a line in an ARP table based on regex
	```Python
	import re
	from netmiko import ConnectHandler
	import getpass

	net_connect = ConnectHandler(device_type = device, ip = ip_address, username = username, password = password)
	output = net_connect.send_command(commands) 
	try:
		output = re.search(r"(.+?) +(.+?) +(\d+) +(.+ \d+?) +(.+) +(\d+?) +(.)",variable)
		x = output.group(1)
		y = output.group(2,re.I)
		print "The MAC address of IP %s is %s." % (x,y)
		#This will print the IP in mac in the x and y variables
		#The variable is an arp entry in an network switch
		#re.I is used for case insensitivity
	except:
		pass
		#Sometimes, there will be lines that will not match this expression,
		#and return with a NoneType. This will skip those lines

	```