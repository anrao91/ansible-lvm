#!/usr/bin/python

from ansible.module_utils.basic import *
import json
import sys
from ast import literal_eval
#sys.path.insert(name_create,"/home/anusha/Code/modules/name_create")
#import name_create

def lv_run_cmd(module, *args):
    # The arguments for lv commands
    action = args[0]
    disks = args[1]
    lv_name = args[2]
    options = args[3]
    data_align = args[4]
    pool_name = args[5]
    vg_name = args[6]
    pool2_name = args[5]
    # Create an LV
    if action == 'create':
        #format the disks to get the updated pv_list
        upvs_list = checkOutput(disks, "pv")
        #Get the updated vg_list
        ldisks = getVgList(upvs_list)
        ldisks.sort()
        #lv_name = name_create.create(lv_name,"lv")
        lvcreate_cmd = module.get_bin_path('lvcreate', True)
        for ldisk in ldisks:
            lv_name = lv_name_generate(lv_name,module)
            create_cmd = "%s -n %s %s %s"%(lvcreate_cmd, lv_name, options,
                ldisk)
            rc,output,err = module.run_command(create_cmd)
            if rc != 0:
               module.fail_json(msg="Failed executing lv command.",rc=rc, err=err)
        module.exit_json(msg="Created lv successfully")

    elif action == 'convert':
        lvconvert_cmd = module.get_bin_path('lvconvert', True)
        #data_align = chunk size
        convert_cmd = "%s --chunksize %s --thinpool %s/%s --poolmetadata"
        "%s/%s %s"%(lvconvert_cmd, data_align, vg_name,
        pool_name,vg_name,pool2_name, options)
        rc,output,err = module.run_command(convert_cmd)
        if rc != 0:
            module.fail_json(msg="Failed executing lv command.",rc=rc, err=err)
        module.exit_json(msg="Converted lv successfully")

    elif action == 'change':
        lvchange_cmd = module.get_bin_path('lvchange', True)
        change_cmd = "%s %s %s/%s"%(lvchange_cmd, options, pool_name)
        rc,output,err = module.run_command(change_cmd)
        print json.dumps({ "output": output })

    # Remove an LV
    elif action == 'remove':
        for ldisk in ldisks:
            lvremove_cmd = module.get_bin_path('lvremove', True)
            cmd = "%s %s"%(lvremove_cmd, ldisk)
            rc,output,err = module.run_command(cmd)
            #if rc != 0:
            #    module.fail_json(msg="Failed executing lv command.",rc=rc, err=err)

            print json.dumps({ "output": output })
    module.exit_json(msg="Created lv successfully")

def getVgList(upvs_list):
    upvs_list = checkOutput(upvs_list,"pv")
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
        lvmout = subprocess.check_output(["vgs","--noheadings","-olv_name"])

    lvm_list = lvmout.replace(' ','')
    ulvm_list = lvm_list.split('\n')
    ulvm_list.pop()
    if command == "pv":
        ulvm_list = list(set(ulvm_list) & set(disks))
    return ulvm_list

def lv_name_generate(name,module):
    #final_op should have vg_name or lv_name  of the current pvs_list or vgs_list passed to it
    final_op = subprocess.check_output(["vgs", "--noheadings", "-olv_name"])

    final_op = final_op.replace(' ','')
    final_op = final_op.split('\n')
    final_op = filter(None,final_op)
    if name in final_op:
        if (re.match('.*?([0-9]+)$', name)):
            num = re.match('.*?([0-9]+)$', name).group(1)
            name = name.replace(num,'')
            number = int(num)
            number += 1
            name += str(number)
            #module.fail_json(msg=name+"I'm here")
    else:
        name += '1'
            #module.fail_json(msg=name+"This is else")
    return name

def main():
    module = AnsibleModule(
        argument_spec = dict(
            action = dict(choices = ["create", "remove","convert","change"]),
            disks = dict(),
            logical_vol_size = dict(type = 'str'),
            lv_name = dict(type = 'str'),
            virt_size = dict(type = 'str'),
            lv_thin = dict(type = 'str'),
            data_align = dict(type = 'str'),
            pool_name = dict(type = 'str'),
            pool2_name = dict(type = 'str'),
            options = dict(type='str'),
            vg_name = dict(type='str'),
            ),
        )

    action = module.params['action']
    disks = literal_eval(module.params['disks'])
    #disks = ''
    lv_name = module.params['lv_name']
    options = module.params['options']
    vg_name = module.params['vg_name']
    data_align = module.params['data_align']
    pool_name = module.params['pool_name']
    pool2_name = module.params['pool2_name']
    lv_run_cmd(module, action, disks, lv_name, options,
        data_align, pool_name, vg_name, pool2_name)
    sys.exit(0)

main()
