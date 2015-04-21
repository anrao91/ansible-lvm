#!/usr/bin/python

from ansible.module_utils.basic import *
import json
from ast import literal_eval

def lv_run_cmd(module, action, *args):
    # The arguments for lv commands
    disks = args[0]
    lv_name = args[1]
    options = args[2]
    # Create an LV
    if action == 'create':
        #format the disks to get the updated pv_list
        upvs_list = checkOutput(disks,"pv")
        #Get the updated vg_list
        ldisks = getVgList(upvs_list)
        lvcreate_cmd = module.get_bin_path('lvcreate', True)
        create_cmd = "%s %s %s"%(lvcreate_cmd, lv_name, options,
                         ' '.join(ldisks))
        rc,output,err = module.run_command(create_cmd)
        if rc != 0:
           module.fail_json(msg="Failed executing lv command.",rc=rc, err=err)
        print json.dumps({ "output": output })

    # Remove an LV
    elif action == 'remove':
        lvremove_cmd = module.get_bin_path('lvremove', True)
        cmd = "%s %s"%(lvremove_cmd, ' '.join(disks))
        rc,output,err = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg="Failed executing lv command.",rc=rc, err=err)

        print json.dumps({ "output": output })

def getVgList(upvs_list):
    upvs_list = checkOutput(disks,"pv")
    has_lv_list = []
    udisks = []
    final_list = []
    for i in upvs_list:
        has_vg = subprocess.check_output(["pvs",i,"--noheadings","-ovg_name"])
        has_vg = has_vg.replace(" ","").replace("\n","")
        if(has_vg):
            udisks.append(has_vg)
        else:
            continue
    udisks = list(set(udisks))
    for i in udisks:
        #op = subprocess.check_output(["pvs",i,"--noheadings","-ovg_name"])
        #op = op.replace(' ','').replace('\n','')
        has_lv = subprocess.check_output(["vgs",i,"--noheadings","-olv_name"])
        # LV list is created to keep track of lv_names
        has_lv_list = checkOutput(has_lv,"lv")
        has_lv = has_lv.replace(" ","").replace("\n","")
        if(has_lv):
            continue
        else:
            final_list.append(i)

    return final_list

def checkOutput(disks,command):
    if command == "pv":
        lvmout = subprocess.check_output(["pvs", "--noheadings", "-opv_name"])
    elif command == "lv":
        lvmout = subprocess.check_output(["vgs",op,"--noheadings","-olv_name"])

    lvm_list = lvmout.replace(' ','')
    ulvm_list = lvm_list.split('\n')
    ulvm_list.pop()
    if command == "pv":
        ulvm_list = list(set(ulvm_list) & set(disks))
    return ulvm_list

def main():
       module = AnsibleModule(
              argument_spec = dict(
                     action = dict(choices = ["create", "remove"]),
                     disks = dict(),
                     logicalVolSize = dict(type = 'str'),
                     lvname = dict(type = 'str'),
                     virtsize = dict(type = 'str'),
                     lvthin = dict(type = 'str'),
                     options = dict(type='str'),
              ),
       )

       action = module.params['action']
       disks = literal_eval(module.params['disks'])
       lvname = module.paramas['lvname']
       options = module.params['options']
       lv_run_cmd(module, action, disks, lvname, options)

main()