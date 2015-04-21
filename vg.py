#!/usr/bin/python

from ansible.module_utils.basic import *
import json
from ast import literal_eval
import re
import subprocess

def vg_run_cmd(module,action,*args):
    disks = args[0]
    options = args[1]
    vg_name = args[2]
    udisks = []
    if action == 'list':
        cmd = 'vgs'
    #elif action == 'create':
    #    vgcmd = 'vgcreate'
    #    cmd = module.get_bin_path(vgcmd, True)
    #    cmd += vgactions + ['-s', str(pesize), vg_name] + disks

    elif action == 'remove':
        cmd = module.get_bin_path('vgremove', True)
        rc, _, err = module.run_command("%s"%cmd)
        print json.dumps({
        "output": err
        })

    elif action == 'create':
        upvs_list = checkOutput(disks)

        for i in upvs_list:
            has_vg = subprocess.check_output(["pvs",i,"--noheadings","-ovg_name"])
            has_vg = has_vg.replace(" ","").replace("\n","")
            if(has_vg):
                continue
            else:
                udisks.append(i)

        for j in udisks:
            vg_name = vg_name_create(vg_name)
            cmd = ''
            cmd = module.get_bin_path('vgcreate', True)
            cmd += " " + vg_name + " " + j + " " + options
            rc, _, err = module.run_command("%s"%cmd)
            if rc != 0:
                print json.dumps({
                    "output": err
                })
    else:
        cmd = 'vg' + action
        cmd = module.get_bin_path(cmd, True)
        rc, _, err = module.run_command("%s"%cmd)
        print json.dumps({
            "output": err
        })

def vg_name_create(vg_name):
    #final_op should have vg_name of the current pvs_list passed to it
    final_op = subprocess.check_output(["pvs", "--noheadings", "-ovg_name"])
    final_op = final_op.replace(' ','')
    final_op = final_op.split('\n')
    final_op = filter(None,final_op)
    if vg_name in final_op:
        if (re.match('.*?([0-9]+)$', vg_name)):
            num = re.match('.*?([0-9]+)$', vg_name).group(1)
            vg_name = vg_name.replace(num,'')
            number = int(num)
            number += 1
            vg_name += str(number)
        else:
            vg_name += '1'
    return vg_name

def checkOutput(disks):
    pvsout = subprocess.check_output(["pvs", "--noheadings", "-opv_name"])
    pvs_list = pvsout.replace(' ','')
    pvs_list = pvs_list.split('\n')
    pvs_list.pop()
    upvs_list = list(set(pvs_list) & set(disks))
    return upvs_list

def main():
    module = AnsibleModule(
    argument_spec = dict(
        action = dict(choices = ["create", "remove"]),
        disks = dict(required = True),
        force_remove_vg = dict(type = 'str'),
        vg_name = dict(type = 'str',required = True),
        options = dict(type = 'str')
        ),
    )

    vg_name = module.params['vg_name']
    disks = literal_eval(module.params['disks'])
    action = module.params['action']
    options = module.params['options']

    #Logic to check whether the vg name is already present -
    #if yes then create a new vg otherwise continue

    vg_run_cmd(module,action,disks,options,vg_name)

main()
