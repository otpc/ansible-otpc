'''
Created by Kylie Yeung (kylieyeung@col.com.hk) for HKEX OTP-C

Version 2.1

Modified by ST (Rivision 1.0)
'''

# Import required modules
from ansible.module_utils.basic import *
from pyFG import FortiOS, FortiConfig, py23_compat
import re
import sys
import time
import getpass
import datetime

module = AnsibleModule(
    argument_spec=dict(
        host=dict(required=True),
        user=dict(required=False),
        passwd=dict(required=False, default=None),
        file=dict(required=True),
        vdom=dict(required=False)
    ))

args = module.params

host = args['host']
user = args['user']
passwd = args['passwd']
file = args['file']
vdom = args['vdom']

'''
host = sys.argv[1]
vdom = sys.argv[2]
file = sys.argv[3]
user = sys.argv[4]
passwd = sys.argv[5]
'''

if __name__ == '__main__':

#	try:

		d = FortiOS(hostname=host, vdom=vdom, username=user, password=passwd)
		d.open()

		d.load_config(empty_candidate=False)

		results = {}
		results['changed'] = False

		with open (file, "r") as c_file:
			data=c_file.read()

		d.load_config(config_text=data, in_candidate=True)
		
		regexp = re.compile('^(config |edit |set |delete |end$|next$)(.*)')
		current_block = d.candidate_config
		if isinstance(data, py23_compat.string_types):
			output = data.splitlines()
		for line in output:
			if 'uuid' in line:
				continue
			if 'snmp-index' in line:
				continue
			line = line.strip()
			result = regexp.match(line)
			
			#print 'check result'
			
			if result is not None:
				action = result.group(1).strip()
				detail = result.group(2).strip()
				
				if action == 'config' or action == 'edit':
					detail = detail.replace('"', '')
					if detail not in current_block.get_block_names():
						config_block = FortiConfig(detail, action, current_block)
						current_block[detail] = config_block
					else:
						config_block = current_block[detail]
					current_block = config_block
					#print current_block.to_text()
                                        results['current_block'] = current_block.to_text()
				elif action == 'end' or action == 'next':
					current_block = current_block.get_parent()
				elif action == 'delete':
					current_block.del_block(detail)
					#print current_block.to_text()
                                        results['current_block'] = current_block.to_text()
		
		#print d.candidate_config.to_text()

		#print d.compare_config()

                diff = d.compare_config()

                if len(diff) is not 0:
                    results['changed'] = True
                    results['difference'] = diff

		d.commit(force=True)

		d.close()
		module.exit_json(**results)

#	except Exception:
#		print ('Error.')
#		sys.exit()
