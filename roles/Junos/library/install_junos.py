#!/usr/bin/env python

# Copyright (c) 2017, COL Limited
#               2017, Kylie Yeung
#
# All rights reserved.

DOCUMENTATION = '''
---
module: install_junos
author: Kylie Yeung, COL Limited
version_added: "1.0.0"
short_description: Install configuration to junos devices
description:
    - Install configuration to junos devices
requirements:
    - junos-eznc >= 1.2.2
options:
    host:
        description:
            - Set to {{ inventory_hostname }}
        required: true
    user:
        description:
            - Login username
        required: false
        default: $USER
    passwd:
        description:
            - Login password
        required: false
        default: assumes ssh-key active
    file:
        description:
            - Path to the file containing the Junos OS configuration data.
              The file has a C(*.set) extension, the content is treated as 
              Junos OS B(set) commands.
        required: true
    port:
        description:
            - port number to use when connecting to the device
        required: false
        default: 22
'''

EXAMPLES = '''
# load merge a change to the Junos OS configuration using NETCONF

- junos_install_config:
    host={{ inventory_hostname }}
    file=banner.conf
'''

#import logging
from os.path import isfile
import os
from distutils.version import LooseVersion
# from jnpr.junos.exception import *

def installConfig(module):
    args = module.params

    from jnpr.junos import Device
    from jnpr.junos.utils.config import Config
    from jnpr.junos.exception import ConnectError, LockError, CommitError
    import sys
    # import getpass

    dev = Device(host=args['host'], port=args['port'], user=args['user'], password=args['passwd'])

    try:
        dev.open()
    except ConnectError as err:
        msg = 'Unable to connect to {0}'.format(args['host'])
        module.fail_json(msg=msg)
        return

    dev.timeout = 300

    cu = Config(dev)

    results = {}
    results['changed'] = False

    file_path = module.params['file']
    file_path = os.path.abspath(file_path)

    try:
        cu.lock()

    except LockError as err:
        msg = "Unable to lock configuration"
        module.fail_json(msg=msg)

    # load_args = {'path': file_path}
    

    cu.load(path=args['file'], format="set")

    diff = cu.diff()

    if diff is not None:
        results['changed'] = True

    try:
        cu.commit()
    except CommitError as err:
        msg = "Unable to commit configuration"
        module.fail_json(msg=msg)

    dev.close()
    module.exit_json(**results)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            user=dict(required=False),
            passwd=dict(required=False, default=None),
            file=dict(required=True),
            port=dict(required=False, default=22),
        ))

    args = module.params

    # ------------------------------
    # make sure file actually exists
    # ------------------------------

    if not isfile(args['file']):
        module.fail_json(msg="Configuration file not found")
        return
    
    installConfig(module)

from ansible.module_utils.basic import *
main()
