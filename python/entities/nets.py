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
import os
import subprocess
import shutil
from subprocess import call
from subprocess import PIPE

from entities import ListenerEntity
from . import GENERATED_TLS_CERTS_DIR
from . import GENERATED_CONFIG_DIR
from . import YAML_SEPARATOR

class Network(object):
    def __init__(self, routers=None, connectors=None, yaml_output_dir=None):
        self.routers = routers
        self.connectors = connectors
        self.listener = None
        if not yaml_output_dir.endswith("/"):
            self.yaml_output_dir = yaml_output_dir + "/"

    def router_file_name(self, router_id):
        return router_id + ".conf"

    def router_yaml_file_name(self, router_id):
        return router_id + ".yaml"

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

        # contents of the file will be erased.
        if not os.path.exists(GENERATED_CONFIG_DIR):
            os.makedirs(GENERATED_CONFIG_DIR)
        else:
            try:
                shutil.rmtree(GENERATED_CONFIG_DIR)
                os.makedirs(GENERATED_CONFIG_DIR)
            except OSError as e:
                os.makedirs(GENERATED_CONFIG_DIR)

        for router in self.routers:
            file_name = self.router_file_name(router.id)

            p = subprocess.Popen(["../../certs/gen-certs.sh", GENERATED_TLS_CERTS_DIR, router.id.lower()], stdout=PIPE,
                                 universal_newlines=True)
            out = p.communicate()[0]
            router_config_file = GENERATED_CONFIG_DIR + file_name
            with open(router_config_file, "w") as out:
                out.write(router.to_string())
                out.write("\n")

                for ssl_profile in router.sslProfiles:
                    out.write(ssl_profile.to_string())
                    ssl_profile.gen_base64_content()

                # Write default
                self.write_default_listeners(out)

                #Connectors
                connector = self.find_from_connector(router.id)
                # Each router gets one listener
                if self.listener:
                    out.write(self.listener.to_string())
                if connector:
                    out.write("\n")
                    to_router = self.find_router_by_id(connector.to_router)
                    connector.host = to_router.host
                    out.write(connector.to_string())

                connector = self.find_to_connector(router.id)
                if connector:
                    if connector.to_router == router.id:
                        router.has_route = True
                        listener_attrs = {'host': '0.0.0.0', "port": "55672", "role": "inter-router", "saslMechanisms": "EXTERNAL", "authenticatePeer": "yes", 'sslProfile': 'ssl-profile'}
                        listener = ListenerEntity(listener_attrs)
                        out.write("\n")
                        out.write(listener.to_string())

                # Write out the boiler pl;plate addresses
                out.write("\n")
                out.write("\naddress {\n   prefix: closest\n   distribution: closest\n} \naddress { \n   prefix: multicast\n   distribution: multicast\n} \n")


        if not os.path.exists(self.yaml_output_dir):
            os.makedirs(self.yaml_output_dir)
        else:
            try:
                shutil.rmtree(self.yaml_output_dir)
                os.makedirs(self.yaml_output_dir)
            except OSError as e:
                os.makedirs(self.yaml_output_dir)

        for router in self.routers:
            # Now all the router related certs and config files have been created. Create the YAML files.

            yaml_file_name = self.yaml_output_dir + self.router_yaml_file_name(router.id)

            with open(yaml_file_name, "w") as yamlout:
                with open("../../yaml/secrets.yaml", "r") as secretsyaml:
                    content = secretsyaml.read()
                    ssl_profile = router.sslProfiles[0]
                    r_id = router.id.lower()
                    content  = content % (r_id, ssl_profile.base64_cert, r_id, ssl_profile.base64_key, r_id, ssl_profile.base64_password, ssl_profile.base64_ca_cert)
                    yamlout.write(content)
                yamlout.write(YAML_SEPARATOR)

                with open("../../yaml/configmap.yaml", "r") as configmapyaml:
                    content = configmapyaml.read()
                    file_name = self.router_file_name(router.id)
                    with open(GENERATED_CONFIG_DIR + file_name, "r") as router_config:
                        router_content  = router_config.read()
                        content = content %  router_content
                        yamlout.write(content)

                yamlout.write(YAML_SEPARATOR)

                with open("../../yaml/service.yaml", "r") as serviceyaml:
                    for line in serviceyaml:
                        yamlout.write(line)
                yamlout.write(YAML_SEPARATOR)

                with open("../../yaml/deployment.yaml", "r") as deploymentyaml:
                    for line in deploymentyaml:
                        yamlout.write(line)
                yamlout.write(YAML_SEPARATOR)

                with open("../../yaml/route.yaml", "r") as routeyaml:
                    if router.has_route:
                        content = routeyaml.read()
                        content = content % router.host
                        yamlout.write(content)
                        yamlout.write(YAML_SEPARATOR)









