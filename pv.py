#!/usr/bin/python

from ansible.module_utils.basic import *
import json

def pvcreate(cmd,disk):
       """Create a PV"""
       for d in disk:
               rc,output,err = module.run_command("%s %s",cmd,d)
               if rc != 0:
                     module.fail_json(msg="Failed executing pv command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def pvremove(cmd):
       """Remove a PV"""
       rc,output,err = module.run_command(cmd)
       if rc != 0:
              module.fail_json(msg="Failed executing pv command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def vgcreate(vg_create_cmd):
       """Create a VG"""
       rc,output,err = module.run_command("%s",vg_create_cmd)
       if rc != 0:
               module.fail_json(msg="Failed executing vg command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def vgremove(vg_rem_cmd):
       """Remove a VG"""
       rc,output,err = module.run_command(vg_rem_cmd)
       if rc != 0:
              module.fail_json(msg="Failed executing vg command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def lvcreate(lv_create_cmd):
       """Create a Linear LV"""
       rc,output,err = module.run_command("%s",lv_create_cmd)
       if rc != 0:
               module.fail_json(msg="Failed executing lv command.",rc=rc, err=err)

       print json.dumps({ "output": output })

def lvremove(lv_rem_cmd):
       """Remove a LV"""
       rc,output,err = module.run_command(lv_rem_cmd)
       if rc != 0:
              module.fail_json(msg="Failed executing vg command.",rc=rc, err=err)

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
                     vg_name = dict(type = 'str',required = True),
                     lv_size = dict(type = 'str',required = True),
                     lv_vol_path = dict(type = 'str',required = True),
              ),
       )

       option = module.params['option']
       disk = module.params['disk']
       dasize = module.params['dasize']
       lvm_cmd = module.params['lvm_cmd']
       vg_name = module.params['vg_name']
       lv_size = module.params['lv_size']
       lv_vol_path = module.params['lv_vol_path']

       if option == 'create' and lvm_cmd == 'pv':
               pvcmd = 'pvcreate'
               pvcreate_cmd = module.get_bin_path(pvcmd, True)

       elif option == 'remove' and lvm_cmd == 'pv':
               pvcmd = 'pvremove'
               pvremove_cmd = module.get_bin_path(pvcmd, True)

       if option == 'create' and lvm_cmd == 'vg':
               vgcmd = 'vgcreate'
               vgcreate_cmd = module.get_bin_path(vgcmd, True)

       elif option == 'remove' and lvm_cmd == 'vg':
               vgcmd = 'pvremove'
               vgremove_cmd = module.get_bin_path(vgcmd, True)

       if option == 'create' and lvm_cmd == 'lv':
               lvcmd = 'lvcreate'
               lvcreate_cmd = module.get_bin_path(lvcmd, True)

       elif option == 'remove' and lvm_cmd == 'lv':
               lvcmd = 'lvremove'
               lvremove_cmd = module.get_bin_path(lvcmd, True)

       rem_cmd = "%s %s"%(pvremove_cmd,disk)
       vg_create_cmd = "%s %s"%(vgcreate_cmd,pvlist)
       vg_rem_cmd = "%s %s"%(vgremove_cmd,vg_name)
       lv_create_cmd = "%s -L %s %s"%(lvcreate_cmd,lv_size,vg_name)
       lv_rem_cmd = "%s %s"%(lvremove_cmd,lv_vol_path)
       pvcreate(pvcreate_cmd,disk)
       pvremove(rem_cmd)
       vgcreate(vg_create_cmd)
       vgremove(vg_rem_cmd);
       lvcreate(lv_create_cmd)
       lvremove(lv_rem_cmd);


main()
