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
openssl genrsa -aes256 -passout pass:ca-password -out $D/ca.key 4096
openssl req -key $D/ca.key -new -x509 -days 99999 -sha256 -out $D/ca.crt -passin pass:ca-password -subj "/C=US/ST=New York/L=Brooklyn/O=Trust Me Inc./CN=Trusted.CA.com"
