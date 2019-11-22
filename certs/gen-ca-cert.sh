#!/bin/bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
#

##### Create root CA #####

if [  $# -ne 1 ]; then
   echo "Usage: ./gen-ca-cert.sh <absolute-path> - <absolute-path> is the path where the ca certs need to be generated. Example - ./gen-ca-cert.sh /tmp/certs"
   exit 1
fi

D=$1

if [ -d "$D" ]; then
   rm -rf $D
   echo Removed direcotry - $D
   mkdir -p $D
   echo Created direcotry - $D
else
   mkdir -p "$D"
   echo Created direcotry - $D
fi

##### Create root CA #####
openssl genrsa -out $D/ca.key 4096
openssl req -key $D/ca.key -new -x509 -days 99999 -sha256 -out $D/ca.crt  -subj "/C=US/ST=New York/L=Brooklyn/O=Trust Me Inc./CN=skupper-messaging"
