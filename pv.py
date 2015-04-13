#!/usr/bin/python

from ansible.module_utils.basic import *
import json
from ast import literal_eval

def pv_run_cmd(module, action, *args):
    # The arguments for pv commands
    disks = args[0]
    options = args[1]
    # Create a PV
    if action == 'create':
        pvcreate_cmd = module.get_bin_path('pvcreate', True)
        create_cmd = "%s %s %s"%(pvcreate_cmd, options,
                         ' '.join(disks))
        rc,output,err = module.run_command(create_cmd)
        if rc != 0:
           module.fail_json(msg="Failed executing pv command.",rc=rc, err=err)
        print json.dumps({ "output": output })

    # Remove a PV
    elif action == 'remove':
        pvremove_cmd = module.get_bin_path('pvremove', True)
        cmd = "%s %s"%(pvremove_cmd, ' '.join(disks))
        rc,output,err = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg="Failed executing pv command.",rc=rc, err=err)

        print json.dumps({ "output": output })

def main():
       module = AnsibleModule(
              argument_spec = dict(
                     action = dict(choices = ["create", "remove"]),
                     disks = dict(),
                     options = dict(type='str'),
              ),
       )

       action = module.params['action']
       disks = literal_eval(module.params['disks'])
       options = module.params['options']
       pv_run_cmd(module, action, disks, options)

main()
