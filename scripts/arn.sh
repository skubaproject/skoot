#!/bin/bash
#
# Usage: setup-env-arn.sh
set -e

SKUPPER_PUBLIC_CLUSTER_COUNT=${SKUPPER_PUBLIC_CLUSTER_COUNT:-1}
SKUPPER_PRIVATE_CLUSTER_COUNT=${SKUPPER_PRIVATE_CLUSTER_COUNT:-1}
SKUPPER_NAMESPACE=${SKUPPER_NAMESPACE:-"skupper"}
SKUPPER_PUBLIC_CLUSTER_NAME_1=${SKUPPER_PUBLIC_CLUSTER_NAME_1:-"PublicCloud1"}
SKUPPER_PUBLIC_CLUSTER_NAME_2=${SKUPPER_PUBLIC_CLUSTER_NAME_2:-"PublicCloud2"}
SKUPPER_PUBLIC_CLUSTER_NAME_3=${SKUPPER_PUBLIC_CLUSTER_NAME_3:-"PublicCloud3"}
SKUPPER_PRIVATE_CLUSTER_NAME_1=${SKUPPER_PRIVATE_CLUSTER_NAME_1:-"PrivateCloud1"}
SKUPPER_PRIVATE_CLUSTER_NAME_2=${SKUPPER_PRIVATE_CLUSTER_NAME_2:-"PrivateCloud2"}
SKUPPER_PRIVATE_CLUSTER_NAME_3=${SKUPPER_PRIVATE_CLUSTER_NAME_3:-"PrivateCloud3"}
SKUPPER_PUBLIC_CLUSTER_SUFFIX_1=${SKUPPER_PUBLIC_CLUSTER_SUFFIX_1:-"XXXX.devcluster.openshift.com"}
SKUPPER_PUBLIC_CLUSTER_SUFFIX_2=${SKUPPER_PUBLIC_CLUSTER_SUFFIX_2:-"XXXX.devcluster.openshift.com"}
SKUPPER_PUBLIC_CLUSTER_SUFFIX_3=${SKUPPER_PUBLIC_CLUSTER_SUFFIX_3:-"XXXX.devcluster.openshift.com"}
SKUPPER_PRIVATE_CLUSTER_SUFFIX_1=${SKUPPER_PRIVATE_CLUSTER_SUFFIX_1:-"nip.io"}
SKUPPER_PRIVATE_CLUSTER_SUFFIX_2=${SKUPPER_PRIVATE_CLUSTER_SUFFIX_2:-"nip.io"}
SKUPPER_PRIVATE_CLUSTER_SUFFIX_3=${SKUPPER_PRIVATE_CLUSTER_SUFFIX_3:-"nip.io"}
SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_1=${SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_1:-"127.0.0.1"}
SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_2=${SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_2:-"127.0.0.1"}
SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_3=${SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_3:-"127.0.0.1"}

DATADIR=$(mktemp -d /tmp/SKUPPER.XXXXX)
trap "clean_exit $DATADIR" EXIT

function clean_exit(){
    local error_code="$?"
    for job in `jobs -p`
    do
        kill -9 $job
    done
    rm -rf "$1"
    return $error_code
}

function _configure_arn {
    # create router network conf
    str1="SKUPPER_PUBLIC_CLUSTER_NAME_"
    str2="SKUPPER_PUBLIC_CLUSTER_SUFFIX_"
    str3="SKUPPER_PRIVATE_CLUSTER_NAME_"

    if [ ${SKUPPER_PUBLIC_CLUSTER_COUNT} -gt 3 ]
    then
       echo "Maximum 3 public clusters supported, setting count to 3"
       SKUPPER_PUBLIC_CLUSTER_COUNT=3
    fi

    if [ ${SKUPPER_PRIVATE_CLUSTER_COUNT} -gt 3 ]
    then
       echo "Maximum 3 private clusters supported, setting count to 3"
       SKUPPER_PRIVATE_CLUSTER_COUNT=3
    fi

    private=1
    until [ $private -gt ${SKUPPER_PRIVATE_CLUSTER_COUNT} ]
    do
        var1="$str3$private"
        cat >> ${DATADIR}/arn.conf <<EOF
Router ${!var1}
EOF
        ((private++))
    done
    
    public=1
    until [ $public -gt ${SKUPPER_PUBLIC_CLUSTER_COUNT} ]
    do
        var1="$str1$public"
        var2="$str2$public"
        cat >> ${DATADIR}/arn.conf <<EOF
Router ${!var1} inter-router.${SKUPPER_NAMESPACE}.apps.${!var2}
EOF
        private=1
        until [ $private -gt ${SKUPPER_PRIVATE_CLUSTER_COUNT} ]
        do
            var3="$str3$private"
            cat >> ${DATADIR}/arn.conf <<EOF
Connect ${!var3} ${!var1}
EOF
            ((private++))
        done
        ((public++))
    done

    public=1
    until [ $public -gt ${SKUPPER_PUBLIC_CLUSTER_COUNT} ]
    do
        peer=$((public+1))
        until [ $peer -gt ${SKUPPER_PUBLIC_CLUSTER_COUNT} ]
        do
            var1="$str1$public"
            var2="$str1$peer"
            cat >> ${DATADIR}/arn.conf <<EOF
Connect ${!var1} ${!var2}
EOF
            ((peer++))
        done
        ((public++))
    done

    cat >> ${DATADIR}/arn.conf <<EOF
Console ${SKUPPER_PRIVATE_CLUSTER_NAME_1} console.${SKUPPER_NAMESPACE}.${SKUPPER_PRIVATE_CLUSTER_LOCAL_IP_1}.${SKUPPER_PRIVATE_CLUSTER_SUFFIX_1}
EOF
}

_configure_arn
cat ${DATADIR}/arn.conf > /dev/stdout

$*

