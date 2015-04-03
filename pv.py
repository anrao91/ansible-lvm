#!/usr/bin/python

from ansible.module_utils.basic import *
import json

def pvcreate(cmd):
       """Create a PV"""
       rc,output,err = module.run_command(cmd)
       if rc != 0:
              module.fail_json(msg="Failed executing pv command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def pvremove(cmd):
       """Remove a PV"""
       rc,output,err = module.run_command(cmd)
       if rc != 0:
              module.fail_json(msg="Failed executing pv command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def main():
       module = AnsibleModule(
              argument_spec = dict(
                     lvm_cmd = dict(choices = ["pv","vg"]),
                     option = dict(choices = ["create", "remove"]),
                     disk = dict(required=True, type='list'),
                     dasize = dict(required = True, type = 'str'),
                     pvlist = dict(required = True, type = 'list'),
                     force_remove_vg = dict(type = 'str'),
              ),
       )

       option = module.params['option']
       disk = module.params['disk']
       dasize = module.params['dasize']
       lvm_cmd = module.params['lvm_cmd']

       if option == 'create' and lvm_cmd == 'pv':
               pvcmd = 'pvcreate'
               pvcreate_cmd = module.get_bin_path(pvcmd, True)

       elif option == 'remove' and lvm_cmd == 'pv':
               pvcmd = 'pvremove'
               pvremove_cmd = module.get_bin_path(pvcmd, True)

       if option == 'create' and lvm_cmd == 'pv':
               pvcmd = 'pvcreate'
               pvcreate_cmd = module.get_bin_path(pvcmd, True)

       elif option == 'remove' and lvm_cmd == 'pv':
               pvcmd = 'pvremove'
               pvremove_cmd = module.get_bin_path(pvcmd, True)

       create_cmd = "%s %s"%(pvcreate_cmd, disk)
       rem_cmd = "%s"%(pvremove_cmd)

       pvcreate(create_cmd);
       pvremove(rem_cmd);
       vgcreate(vg_create_cmd);
       vgremove(vg_rem_cmd);


main()
