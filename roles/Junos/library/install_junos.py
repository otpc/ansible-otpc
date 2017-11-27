'''
Created by Kylie Yeung (kylieyeung@col.com.hk) for HKEX OTP-C

Version 2.0

Modified by ST (Revision 1.0)

'''

from ansible.module_utils.basic import *
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *
import sys
import getpass
import time
import datetime

module = AnsibleModule(
    argument_spec=dict(
        host=dict(required=True),
        user=dict(required=False),
        passwd=dict(required=False, default=None),
        file=dict(required=True),
        port=dict(required=False, default=22),
    ))

args = module.params

host = args['host']
port = args['port']
file = args['file']
user = args['user']
passwd = args['passwd']

'''
host = sys.argv[1]
port = sys.argv[2]
file = sys.argv[3]
user = sys.argv[4]
passwd = sys.argv[5]
'''

def InstallConfig():

	dev = Device(host=host, port=port, user=user, password=passwd)

	try:
		dev.open()
	except ConnectError as err:
		#print('Error: ' + repr(err))
                msg = 'Unable to connect to {0}'.format(args['host'])
                module.fail_json(msg=msg)
                return

	dev.timeout = 300

	cu = Config(dev)

        results = {}
        results['changed'] = False

	try:
		cu.lock()
	except LockError as err:
		#print ("Error: Unable to lock configuration")
                msg = 'Unable to lock configuration'
                module.fail_json(msg=msg)
                return

	cu.load(path=file, format="set")

	try:
		cu.commit()
		#print ('Commit successful')
                results['commit'] = "successful"
	except RpcError as err:
		#print ('Commit error')
                msg = "Commit error"
                module.fail_json(msg=msg)
                return

	diff = cu.diff(rb_id=1)

        if diff is not None:
            results['changed'] = True

	#print ("Compare the difference after commit change")
	#print diff   #this diff variable will be string of the difference. You can parse accordingly to achieve verification
        results['difference'] = diff

	cu.unlock()

	dev.close()
	module.exit_json(**results)


def Main():

	InstallConfig()

if __name__ == '__main__':
	try:
		Main()
	except KeyboardInterrupt:
		pass
