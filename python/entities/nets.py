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

import subprocess
from subprocess import call
from subprocess import PIPE

from entities import ListenerEntity

class Network(object):
    def __init__(self, routers=None, connectors=None):
        self.routers = routers
        self.connectors = connectors
        self.listener = None

    def router_file_name(self, router_id):
        return router_id + ".conf"

    def find_to_connector(self, router_id):
        if not self.connectors:
            return
        for connector in self.connectors:
            if connector.to_router == router_id:
                return connector
        return None

    def find_from_connector(self, router_id):
        if not self.connectors:
            return
        for connector in self.connectors:
            if connector.from_router == router_id:
                return connector
        return None

    def find_router_by_id(self, router_id):
        maching_router = None
        for router in self.routers:
            if router.id == router.id:
                maching_router = router
                break
        return maching_router

    def generate_router_configs(self):
        # Kick off the script that creates the certificate authority
        #subprocess.Popen(['../../certs/gen-ca-cert.sh'], shell=True)
        #subprocess.Popen(["bash", "../../certs/gen-ca-cert.sh"])

        p = subprocess.Popen(["../../certs/gen-ca-cert.sh"], stdout=PIPE, universal_newlines=True)
        out = p.communicate()[0]

        for router in self.routers:
            file_name = self.router_file_name(router.id)
            p = subprocess.Popen(["../../certs/gen-certs.sh", router.id.lower()], stdout=PIPE,
                                 universal_newlines=True)
            #subprocess.Popen(

            #       ["bash", "../../certs/generate-certs.sh", router.id])
            # contents of the file will be erased.
            with open("../../generated-router-configs/" + file_name, "w") as out:
                out.write(router.to_string())
                out.write ("\n")
                listener = ListenerEntity()
                listener.defaults()
                out.write(listener.to_string())
                out.write("\n")
                listener = ListenerEntity()
                listener.http_defaults()
                out.write(listener.to_string())
                connector = self.find_from_connector(router.id)
                # Each router gets one listener
                if self.listener:
                    out.write(self.listener.to_string())
                if connector:
                    out.write("\n")
                    router = self.find_router_by_id(connector.to_router)
                    connector.host = router.host
                    out.write(connector.to_string())

                connector = self.find_to_connector(router.id)
                if connector:
                    if connector.to_router == router.id:
                        listener_attrs = {'host': '0.0.0.0', "port": "55672", "role": "inter-router", "saslMechanisms": "EXTERNAL", "authenticatePeer": "yes"}
                        listener = ListenerEntity(listener_attrs)
                        out.write("\n")
                        out.write(listener.to_string())

                # Write out the boiler pl;plate addresses
                out.write("\n")
                out.write("\naddress {\n   prefix: closest\n   distribution: closest\n} \naddress { \n   prefix: multicast\n   distribution: multicast\n} \n")


