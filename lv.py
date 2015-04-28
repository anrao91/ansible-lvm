#!/usr/bin/python

from ansible.module_utils.basic import *
import json
import sys
from ast import literal_eval
import subprocess
from math import floor

def rhs_lv_params_compute(vgname):
    # These are the parameters computed for RHS volumes
    global dataalign, stripe_element, pvname, pvsize, metadatasize
    dataalign = stripesize = 1280 # In kb
    stripe_element = 128          # In kb
    # Currently handles only one pv
    pvname = subprocess.check_output(["vgs", vgname, "--noheadings",
                                      "-opv_name"]).strip()
    pvsize = subprocess.check_output(["pvs", pvname, "--noheadings",
                                      "--units", "m", "-opv_size"]).strip()
    pvsize = floor(float(pvsize.replace('m', '')) - 4)
    KB_PER_GB=1048576
    if pvsize > 1000000:
        METADATA_SIZE_GB=16
        metadatasize = floor(METADATA_SIZE_GB * KB_PER_GB)
    else:
        METADATA_SIZE_MB = pvsize / 200
        metadatasize = floor(METADATA_SIZE_MB) * 1024
    metadatasize = floor(metadatasize)

def lvcreate(module, lvname, lvtype, vgname, poolname=''):
    # TODO: This is sort of a hack, do it more elegantly
    lv_bin = module.get_bin_path('lvcreate', True)
    if lvtype == "thin":
        poolsize = (pvsize * 1024) - metadatasize
        floor(poolsize)
        lvcreate_cmd = "%s -L %sK --name %s %s"%(lv_bin, poolsize, lvname,
                                                 vgname)
    elif lvtype == "thick":      # thick lv
        lvcreate_cmd = "%s -L %sK --name %s %s"%(lv_bin, metadatasize, lvname,
                                                 vgname)
    elif lvtype == "virtual":
        poolsize = (pvsize * 1024) - metadatasize
        floor(poolsize)
        lvcreate_cmd = "%s -V %sK -T /dev/%s/%s --name %s"%(lv_bin, poolsize,
                                                            vgname, poolname,
                                                            lvname)
    # module.fail_json(msg=lvcreate_cmd)
    rc, output, err = module.run_command(lvcreate_cmd)
    if rc == 0:
        changed = True
    else:
        module.fail_json(msg="Failed to create %s"%lvname)
    if changed == True:
        module.exit_json(changed=True, lv=lvname)

def lvconvert(module, chunksize, thinpool, poolmetadata, poolmetadataspare):
    lv_bin = module.get_bin_path('lvconvert', True)
    # This is quite a hack, do it more cleanly
    lvconvert_cmd = "%s --yes -ff --chunksize %sk --thinpool %s --poolmetadata \
     %s --poolmetadataspare %s"%(lv_bin, dataalign, thinpool, poolmetadata,
                             poolmetadataspare)
    rc, output, err = module.run_command(lvconvert_cmd)
    if rc == 0:
        changed = True
    else:
        module.fail_json(msg="Failed to lvconvert %s"%thinpool)
    if changed == True:
        module.exit_json(changed=True, lv=thinpool)

def lvchange(module, zero, vgname, poolname):
    lv_bin = module.get_bin_path('lvchange', True)
    lvchange_cmd = "%s --zero %s %s/%s"%(lv_bin, zero, vgname, poolname)
    rc, output, err = module.run_command(lvchange_cmd)
    if rc == 0:
        changed = True
    else:
        module.fail_json(msg="Failed to change %s/%"%(vgname, poolname))
    if changed == True:
        module.exit_json(changed=True, lv=vgname)

def lvremove(lvname, vgname):
    lv_bin = module.get_bin_path('lvremove', True)
    lvremove_cmd = "%s -ff --yes %s/%s"%(vgname,lvname)
    rc, output, err = module.run_command(lvremove_cmd)
    if rc == 0:
        changed = True
    else:
        module.fail_json(msg="Failed to remove %s"%lvpath)
    if changed == True:
        module.exit_json(changed=True, lv=lvname)

def main():
    module = AnsibleModule(
        argument_spec = dict(
            action = dict(choices = ["create", "remove", "convert", "change"]),
            lvname = dict(type = 'str'),
            lvtype = dict(type = 'str'),
            vgname = dict(type = 'str', required = True),
            poolname = dict(type = 'str'),
            lvsize = dict(type = 'str'),
            compute = dict(type = 'str'),
            chunksize = dict(type = 'str'),
            thinpool = dict(type = 'str'),
            poolmetadata = dict(type = 'str'),
            poolmetadataspare = dict(type = 'str'),
            zero = dict(type = 'str'),
            lvpath = dict(type = 'str'),
        ),
    )

    action = module.params['action']
    lvname = module.params['lvname']
    lvtype = module.params['lvtype']
    vgname = module.params['vgname']
    poolname = module.params['poolname']
    lvsize = module.params['lvsize']
    compute = module.params['compute']
    chunksize = module.params['chunksize']
    thinpool = module.params['thinpool']
    poolmetadata = module.params['poolmetadata']
    poolmetadataspare = module.params['poolmetadataspare']
    zero = module.params['zero']
    lvpath = module.params['lvpath']

    if action == 'create':
        # TODO: validate the params
        # if (compute is None or compute == '' or compute == 'no')
        # and lvsize = ''
        if compute == 'rhs' and (poolname == '' or poolname is None):
            rhs_lv_params_compute(vgname)
            lvcreate(module, lvname, lvtype, vgname)
        elif compute == 'rhs' and (poolname != '' or poolname is not None):
            rhs_lv_params_compute(vgname)
            lvcreate(module, lvname, lvtype, vgname, poolname=poolname)
        else:
            # TODO: create a lv with just the given parameters
            pass

    if action == 'remove':
        lvremove(lvname, vgname)

    if action == 'convert':
        rhs_lv_params_compute(vgname)
        lvconvert(module, chunksize, thinpool, poolmetadata, poolmetadataspare)

    if action == 'change':
        lvchange(module, zero, vgname, poolname)

main()
