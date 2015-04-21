#!/usr/bin/python

import re
import subprocess

def create(name,command):
    #final_op should have vg_name or lv_name  of the current pvs_list or vgs_list passed to it
    if(command == 'vg'):
        final_op = subprocess.check_output(["pvs", "--noheadings", "-ovg_name"])
    if(command == 'lv'):
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
        else:
            name += '1'
    return name

