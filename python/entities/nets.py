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
from . import GENERATED_TLS_CERTS_DIR
from . import GENERATED_CONFIG_DIR

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

    def write_default_listeners(self, out):
        """
        Writes out listerns on ports amqp and 8672 (http)
        :param out:
        :return:
        """
        out.write("\n")
        # A default listener on port amqp for every router
        listener = ListenerEntity()
        listener.defaults()
        out.write(listener.to_string())
        out.write("\n")

        # A HTTP listener for all routers
        listener = ListenerEntity()
        listener.http_defaults()
        out.write(listener.to_string())

    def generate_router_configs(self):
        # Kick off the script that creates the certificate authority
        p = subprocess.Popen(["../../certs/gen-ca-cert.sh", GENERATED_TLS_CERTS_DIR], stdout=PIPE, universal_newlines=True)
        out = p.communicate()[0]

        for router in self.routers:
            file_name = self.router_file_name(router.id)
            p = subprocess.Popen(["../../certs/gen-certs.sh", GENERATED_TLS_CERTS_DIR, router.id.lower()], stdout=PIPE,
                                 universal_newlines=True)
            out = p.communicate()[0]

            # contents of the file will be erased.
            with open(GENERATED_CONFIG_DIR +  file_name, "w") as out:
                out.write(router.to_string())
                out.write("\n")

                for ssl_profile in router.sslProfiles:
                    out.write(ssl_profile.to_string())

                # Write default
                self.write_default_listeners(out)

                #Connectors
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
                        listener_attrs = {'host': '0.0.0.0', "port": "55672", "role": "inter-router", "saslMechanisms": "EXTERNAL", "authenticatePeer": "yes", 'sslProfile': 'ssl-profile'}
                        listener = ListenerEntity(listener_attrs)
                        out.write("\n")
                        out.write(listener.to_string())

                # Write out the boiler pl;plate addresses
                out.write("\n")
                out.write("\naddress {\n   prefix: closest\n   distribution: closest\n} \naddress { \n   prefix: multicast\n   distribution: multicast\n} \n")

            # Now all the router related certs and config files have been created. Create the


