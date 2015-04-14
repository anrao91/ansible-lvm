#!/usr/bin/python

from ansible.module_utils.basic import *
import json

def vg_runcmd(action,*args):
    dev_list = args[0]
    pesize = args[1]
    if action == 'list':
        cmd = 'vgs'
    elif option == 'create':
        vgcmd = 'vgcreate'
        cmd = module.get_bin_path(vgcmd, True)
        cmd += vgoptions + ['-s', str(pesize), vg_name] + dev_list

    elif option == 'remove':
        vgcmd = 'pvremove'
        cmd = module.get_bin_path(vgcmd, True)
        cmd += vg_name
    else:
        cmd = 'vg' + action
        cmd = module.get_bin_path(cmd, True)

    rc, _, err = module.run_command("%s"%(cmd))
    print json.dumps({
    "output": err
    })


def main():
    module = AnsibleModule(
    argument_spec = dict(
        option = dict(choices = ["create", "remove"]),
        dev_list = dict(required = True, type = 'list'),
        force_remove_vg = dict(type = 'str'),
        vg_name = dict(type = 'str',required = True),
        dev_list = dict(type = 'list',required = True),
        pe_size = dict(type = 'str', default = '4MiB'),
              ),
       )

    vg_name = module.params['vg_name']
    dev_list = module.params['dev_list']
    pe_size = module.params['pe_size']

    #Logic to check whether the vg name is already present -
    #if yes then create a new vg otherwise continue

    op = subprocess.check_output('vgs')
    final_op =  (op.split('\n'))[1].split(' ')
    if final_op == vg_name:
        num = re.match('.*?([0-9]+)$', vg_name).group(1)
        num += 1
        vg_name += str(num)


        vg_run_cmd(option,dev_list,pesize)


main()
