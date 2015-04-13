#!/usr/bin/python

from ansible.module_utils.basic import *
import json

def vg_runcmd(action,dev_list,arg = ''):
    if action == 'list':
        cmd = 'vgs'
    elif action == 'check':
        cmd = 'pvchk'
    else:
        cmd = 'pv' + action

    cmdpath = module.get_bin_path(cmd, True)
    rc, _, err = module.run_command("%s %s %s"%(cmd, args))
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

''' Logic to check whether the vg name is already present -
    if yes then create a new vg otherwise continue'''

    op = subprocess.check_output('vg')
    final_op =  (op.split('\n'))[1].split(' ')
    if final_op == vgname:
        num = re.match('.*?([0-9]+)$', vgname).group(1)
        num += 1
        vgname += str(num)


    if option == 'create':
        vgcmd = 'vgcreate'
        vgcreate_cmd = module.get_bin_path(vgcmd, True)
        vgcreate_cmd += vgoptions + ['-s', str(pesize), vg_name] + dev_list

        vgcmd = 'pvremove'
        vgremove_cmd = module.get_bin_path(vgcmd, True)
        vg_remove_cmd += vg_name
    vgcreate(vgcreate_cmd)
    vgremove(vg_remove_cmd);


main()
