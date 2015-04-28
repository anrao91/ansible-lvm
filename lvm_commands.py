#!/usr/bin/python

DOCUMENTATION="""
---
module: pv
short_description: Manage physical volumes.
description:
  - This module provides the functions to manage the physical volumes on a
    machine.
  - Implements the pv* family of commands.

version_added: "0.1"
options:
  action:
    description:
      - Description of the command called
        Possible actions: list, create, check, change, display, move, remove,
                          resize, scan
    default: list
    required: true
  devices:
    description:
      - The physical devices on which the action to be carried out
    required: false
    default: none
  options:
    description:
      - The options string which will be passed to the action.
    required: false
    default: null
"""

def pv_runcmd(module, action, device, args = ''):
    if action == 'list':
        cmd = 'pvs'
    elif action == 'check':
        cmd = 'pvchk'
    else:
        cmd = 'pv' + action

    cmdpath = module.get_bin_path(cmd, True)
    rc, _, err = module.run_command("%s %s %s"%(cmd, args, device))
    print json.dumps({
    "output": err
    })

def vg_runcmd(module, action, device, args = ''):
    if action == 'list':
            cmd = 'vgs'
    elif action == 'check':
            cmd = 'vgchk'
    else:
            cmd = 'vg' + action
    cmdpath = module.get_bin_path(cmd, True)
    rc, _, err = module.run_command("%s %s %s"%(cmd, args, device))
    print json.dumps({
            "output": err})

def lv_runcmd(module, action, device, args = ''):
    if action == 'list':
            cmd = 'lvs'
    else:
            cmd = 'lv' + action
    cmdpath = module.get_bin_path(cmd, True)
    rc, _, err = module.run_command("%s %s %s"%(cmd, args, device))
    print json.dumps({
    "output": err})
def main():
    """Validate and call the function mentioned in playbook.

    Example playbook entry:
    pv: action=create device={{ device_list }}
        options = "--dataalignment 128k"
    """

    module = AnsibleModule(
        argument_spec = dict(
            action = dict(required=True, type='str',
                          choices=['list', 'create', 'check', 'change',
                                   'convert','display', 'move', 'remove',
                                   'resize', 'scan']),
            device = dict(required=False),
            options = dict(required=False, type='str'),
           """ Options include all the params not mentioned in the
               command - i.e. data-alignment size, vg_name,
               force-remove option, etc
           """
        ),
    )

    action = module.params['action']
    device = module.params['device']
    options = module.params['options']

    pv_runcmd(module, action, device, options)

from ansible.module_utils.basic import *
main()
