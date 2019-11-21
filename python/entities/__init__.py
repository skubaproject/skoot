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
# under the License.
#

GENERATED_INTERNAL_TLS_CERTS_DIR = "/tmp/qpid-dispatch-certs/internal/"
MOUNTED_INTERNAL_TLS_CERTS_DIR = "/etc/qpid-dispatch-certs/skupper-internal/"

GENERATED_EXTERNAL_TLS_CERTS_DIR = "/tmp/qpid-dispatch-certs/external/"
MOUNTED_EXTERNAL_TLS_CERTS_DIR = "/etc/qpid-dispatch-certs/skupper-amqps/"

GENERATED_CONFIG_DIR="/tmp/qpid-dispatch-configs/"
MOUNTED_CONFIG_DIR="/etc/qpid-dispatch/"
ENTITY_INDENT = "            "
ATTRIBUTE_INDENT = "                "

YAML_SEPARATOR = "\n---\n"