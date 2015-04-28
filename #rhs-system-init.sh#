#!/bin/bash
# Title : rhs-system-init.sh
# Author : Veda Shankar
# Description :
# RHS system initialization script.  The script is supposed to be run after
# ISO installtion and setting up the network.
# The script does the following:
#     - Identify the RAID volume using the WWID and create a brick.
#     - Based on the use case, run the corresponding performance tuning
#       profile.
#     - Register with RHN and subscribe to correct software channels.
#     - Run yum update to apply the latest updates.
#
# History:
# 12/13/2012 Veda Shankar  Created
# 12/20/2012 Veda : Check the correct RHN channels before applying updates
# 01/18/2013 Veda : Incorporate recommended options for pv create, mkfs and
#                   mounting.
# 01/24/2013 Veda : Provide -n option for dry-run.
# 04/15/2013 Veda : Additional performance options for mkfs and fstab.
# 05/01/2013 Veda : Use lvmdiskscan to detect disks
#                   Auto detect whether physical or virtual.
#                   Changed the inode size to 512 for object use case.
#                   Set the performance profile to rhs-virtualization for
#                   virtual workload.
# 05/22/2013 Veda : Made sure that mkfs and fstab mount options follow the
#                   latest recommendations for XFS parameters for RHS bricks.
# 08/27/2013 Veda : Provide -r option to skip RHN registration.
# 08/27/2013 Veda : Register with RHS 2.1 and RHEL 6.4.z channels.
# 06/07/2014 Veda : Added support for thinly provisioned logical volumes
#                   which is a requirement to support snapshots feature
#                   in RHS 3.0.
# 06/07/2014 Veda : Also, skipping RHN registration by default as RHS 3.0
#                   uses CDN. No support for registering with CDN in this
#                   version.
# 08/20/2014 Veda : ThinLV creation based on latest recommendation.
# 11/20/2014 BenT : Update brick config for current thinp recommendations.
#

# Default settings
ME=$(basename $0);
dryrun=0
skip_registration=1
logfile=/root/rhs-init.log
vgname_base=RHS_vg
lvname_base=RHS_lv
poolname_base=RHS_pool
brickpath=/rhs
workload=general
inode_size=512
tune_profile=rhs-high-throughput

# RAID related variables.
# stripesize - RAID controller stripe unit size
# stripe_elements - the number of data disks
# The --dataalignment option is used while creating the physical volumeTo
# align I/O at LVM layer
# dataalign -
# RAID6 is recommended when the workload has predominanatly larger
# files ie not in kilobytes.
# For RAID6 with 12 disks and 128K stripe element size.
stripesize=128k
stripe_elements=10
dataalign=1280k

# RAID10 is recommended when the workload has predominanatly smaller files
# i.e in kilobytes.
# For RAID10 with 12 disks and 256K stripe element size, uncomment the
# lines below.
# stripesize=256k
# stripe_elements=6
# dataalign=1536k

#
fs_block_size=8192
percent_inodes=15
xfs_alloc_groups=64

# Disk path name variables
disk_path=NODISK
root_disk_path=NODISK

#exec > >(tee /root/rhs-init.log)
#exec 2>&1

function usage {
    cat <<EOF
Usage:  $ME [-h] [-u virtual|object]

General:
  -u <workload>   virtual - RHS is used for storing virtual machine images.
                  object  - Object Access (HTTP) is the primary method to
                            access the RHS volume.
                  The workload helps decide what performance tuning profile
                  to apply and other customizations.
                  By default, the  general purpose workload is assumed.
  -d <block dev>  Specify a preconfigured block device to use for a brick.
                  This must be the full path and it should already have an
                  XFS file system.  This is used when you want to manually
                  tune / configure your brick.  Example:
                  $ME -d /dev/myLV/myVG
  -n              Dry run to show what devices will be used for brick creation.
  -r              Skip RHN Registration.
  -h              Display this help.

EOF
    exit 1
}


function quit {
    exit $1
}

function yesno {
   while true; do
       read -p "$1 " yn
       case $yn in
           [Yy]* ) return 0;;
           [Nn]* ) return 1;;
           * ) echo "Please answer yes or no.";;
       esac
   done
}


function create_pv {
    dev=$1
    pvdisplay | grep -wq $dev
    ret=$?
    if [ $ret -eq 0 ]
    then
        echo "$dev Physical Volume exits!"
        return 1
    fi
    echo "Create Physical Volume with device $dev"
    [ $dryrun -eq 1 ] && return 0

    pvcreate --dataalignment $dataalign $dev
    return  $?
}

function create_vg {
    dev=$1
    vgname=$2
    echo "Create Volume Group $vgname."
    [ $dryrun -eq 1 ] && return 0

    vgcreate --physicalextentsize $stripesize $vgname $dev
    return  $?
}


function create_lv {
    vgname=$1
    lvname=$2
    pvname=$3
    poolname=$4
    KB_PER_GB=1048576
    # STRIPESIZE is 128 * 10
    STRIPESIZE=$(echo $dataalign | cut -d k -f 1)
    STRIPE_ELEMENT_KB=$(echo $stripesize | cut -d k -f 1)

    echo "Create Logical Volume $lvname."
    [ $dryrun -eq 1 ] && return 0

    pvsize=`pvs --noheading --units m  -o pv_size $pvname | cut -f1 -d"m"`
    pvsize=`echo "($pvsize - 4) * 100 / 100" | bc`

    if [ $pvsize -gt 1000000 ]
    then
        METADATA_SIZE_GB=16
        (( metadatasize = $METADATA_SIZE_GB * $KB_PER_GB / $STRIPESIZE ))
        (( metadatasize = $metadatasize * $STRIPESIZE ))
    else
        METADATA_SIZE_MB=`echo "$pvsize / 200" | bc`
        (( metadatasize = $METADATA_SIZE_MB * 1024 / $STRIPESIZE ))
        (( metadatasize = $metadatasize * $STRIPESIZE ))
    fi

    # create metadata LV that has a size which is a multiple of RAID stripe
    # width
    lvcreate -L ${metadatasize}K --name metadata $vgname || return $?

    # create data LV that has a size which is a multiple of stripe width
    ((pool_sz = $pvsize  * 1024 / $STRIPESIZE))
    ((pool_sz = $pool_sz * $STRIPESIZE))
    ((pool_sz = $pool_sz - $metadatasize))
    echo "Creating a ${pool_sz} KB thin pool named $poolname"
    lvcreate -L ${pool_sz}K --name $poolname $vgname || return $?

    # create thin-pool without creating a spare metadata area
    # (though spare metadata area is useful if/when thin-pool metadata repair
    # is needed)
    # -- NOTE: could also use --chunksize 256K or 128K here since they are a
    # factor of stripe width
    lvconvert --chunksize $dataalign --thinpool $vgname/$poolname \
        --poolmetadata $vgname/metadata --poolmetadataspare n || return $?

    # create stripe-aligned thin volume:
    lvcreate -V ${pool_sz}K -T /dev/$vgname/$poolname -n $lvname || return $?
    lvchange --zero n $vgname/$poolname
    return  $?
}

function old_create_lv {
    vgname=$1
    lvname=$2
    pvname=$3
    poolname=$4

    echo "Create Logical Volume $lvname."
    [ $dryrun -eq 1 ] && return 0

    pvsize=`pvs --noheading --units M  -o pv_size $pvname | cut -f1 -d"M"`
    metadatasize=`echo "$pvsize / 1000" | bc`
    lvcreate -l 100%FREE -c 1M --poolmetadatasize $metadatasize \
        -T /dev/$vgname/$poolname
    virtualsize=`lvs --noheading --units M -o lv_size /dev/$vgname/$poolname`
    lvcreate -V${virtualsize} -T /dev/$vgname/$poolname -n $lvname
    return  $?
}

function create_fs {
    vgname=$1
    lvname=$2
    echo "Create XFS file system /dev/$vgname/$lvname."
    echo "mkfs -t xfs -f -K -i size=$inode_size -d \
sw=$stripe_elements,su=$stripesize -n size=$fs_block_size /dev/$vgname/$lvname"
    [ $dryrun -eq 1 ] && return 0

    mkfs -t xfs -f -K -i size=$inode_size -d \
        sw=$stripe_elements,su=$stripesize -n size=$fs_block_size \
        /dev/$vgname/$lvname
    return  $?
}

function create_fstab_entry {
    [ $dryrun -eq 1 ] && return 0
    vgname=$1
    lvname=$2
    mount=$3
    echo "Create fstab entry for /dev/$vgname/$lvname."
    echo "/dev/$vgname/$lvname  $mount           xfs \
        inode64,noatime,nodiratime 1 2" >> /etc/fstab
    return 0
}

function create_bricks {

    declare -a device_name=(`lvmdiskscan | grep $disk_path \
                              | grep -v $root_disk_path | awk '{ print $1 }'`)
    echo "brick devices:"
    echo ${device_name[*]}
    count=0
    dev_count=1
    for dev in "${device_name[@]}"
    do
       echo "---- Device# ${dev_count} ----"
       vgname=$vgname_base$dev_count
       lvname=$lvname_base$dev_count
       poolname=$poolname_base$dev_count

       # Create Physical Volume
       create_pv $dev || exit 1

       # Create Volume Group
       create_vg $dev $vgname || exit 1

       # Create Logical Group
       create_lv $vgname $lvname $dev $poolname || exit 1

       # Create XFS file system
       create_fs $vgname $lvname || exit 1

       # Make directory for brick mount point
       [ $dryrun -eq 0 ] && mkdir -p $brickpath/brick$dev_count

       # Create entry in /etc/fstab
       create_fstab_entry $vgname $lvname $brickpath/brick$dev_count || exit 1

       # Mount all the bricks.
       [ $dryrun -eq 0 ] && mount -a

       (( count++ ))
       (( dev_count++ ))
            echo
    done
}

function use_specified_device {
    # Make directory for brick mount point
    [ $dryrun -eq 0 ] && mkdir -p $brickpath/brick1

    # Create entry in /etc/fstab
    echo "Create fstab entry for ${1}."
    [ $dryrun -eq 0 ] && echo "${1} $brickpath/brick1 xfs inode64,noatime,\
nodiratime 1 2" >> /etc/fstab

    # Mount all the bricks.
    [ $dryrun -eq 0 ] && mount -a
}

function tune_performance {

    echo "---- Performance tune for $workload storage ----"
    tuned-adm profile $tune_profile
}


function channels_error {
   declare -a reg_channels=(`rhn-channel --list`)
   echo "ERROR: All required channels are not registered!"
   echo -e "Required Channels:\n\trhel-x86_64-server-6.4.z\n\t\
rhel-x86_64-server-sfs-6.4.z\n\trhel-x86_64-server-6-rhs-2.1"
   echo -e "Registered Channels:"
   for chan in "${reg_channels[@]}"
   do
         echo -e "\t$chan"
   done
   return 1
}


function check_channels {

   declare -a reg_channels=(`rhn-channel --list`)
   if [ ${#reg_channels[@]} -lt 3 ]
   then
      channels_error
      return 1
   fi

   correct=0
   for chan in "${reg_channels[@]}"
   do
      if [ "$chan" == "rhel-x86_64-server-6.4.z" \
           -o "$chan" == "rhel-x86_64-server-sfs-6.4.z" \
           -o "$chan" == "rhel-x86_64-server-6-rhs-2.1" \
         ]
      then
         (( correct++ ))
      fi
   done

   if [ $correct -ne 3 ]
   then
      channels_error
      return 1
   fi

   echo -e "Registered Channels:"
   for chan in "${reg_channels[@]}"
   do
         echo -e "\t$chan"
   done
   return 0
}


function rhn_register_update {

    profile_name=`hostname -s`
    profile_name=RHS_$profile_name
    rhn_register

    echo "---- Register Channels ----"
    read -p "RHN Login: " rhn_login
    read -s -p "RHN Password: " rhn_password
    echo ""
    rhn-channel --verbose --user $rhn_login --password $rhn_password \
        --add --channel=rhel-x86_64-server-sfs-6.4.z
    rhn-channel --verbose --user $rhn_login --password $rhn_password \
        --add --channel=rhel-x86_64-server-6-rhs-2.1

    check_channels || return 1
    echo "System registered to the correct Red Hat Channels!"
    if yesno "Do you want to apply updates now? "
    then
        echo "---- Apply Updates ----"
        yum -y update
    fi
}


function main {

    while getopts :r:n:d:h:u: OPT; do
    case "$OPT" in
        u)
            case $OPTARG in
                object)
                    workload=$OPTARG
                    inode_size=256
                    ;;
                virtual)
                    workload=$OPTARG
                    tune_profile=rhs-virtualization
                    ;;
                *)
                    echo "Unrecognized option."
                    usage # print usage and exit
            esac
            ;;
        n)
	    dryrun=1
            ;;
        r)
	    skip_registration=1
            ;;
        d)
        device_name_in=$OPTARG
            ;;
        h)
	    usage # print usage and exit
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
	    usage # print usage and exit
            ;;
        :)
            echo "Option -$OPTARG requires an argument."
            usage # print usage and exit
            ;;
    esac
    done
    echo "Setting workload to $workload."

    # Check whether it is a physical or a virtual deployment
    tempvar=(`lvmdiskscan | grep /dev/sda`)
    ret=$?
    if [ $ret -eq 0 ]
    then
        echo "Physical deployment!"
        disk_path=/dev/sd
        root_disk_path=/dev/sda
    else
         tempvar=(`lvmdiskscan | grep /dev/vda`)
         ret=$?
         if [ $ret -eq 0 ]
         then
             echo "Virtual deployment!"
             disk_path=/dev/vd
             root_disk_path=/dev/vda
         fi
    fi

    if [ "$disk_path" == "NODISK" ] && [ -z $device_name_in ]
    then
        echo "Unknown Deployment : Could not find physical (/dev/sda) \
or virtual (/dev/vda) devices!"
        echo "exiting ..."
        return 1
    fi

    # Brick creation, if preconfigured brick is specified
    if [ -z $device_name_in ]
    then
        create_bricks
    else
        use_specified_device $device_name_in
    fi

    # If dry run then exit
    [ $dryrun -eq 1 ] && return 0

    # Invoke tuned profile
    tune_performance

    # Register and update with RHN
    if [ $skip_registration -ne 1 ]
    then
        rhn_register_update
    fi

}

# Call Main
main "$@";
