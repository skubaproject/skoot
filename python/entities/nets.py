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
import json
import base64
from subprocess import call
from subprocess import PIPE
import random, string

from .entities import ListenerEntity
from . import GENERATED_INTERNAL_TLS_CERTS_DIR
from . import GENERATED_CONFIG_DIR
from . import YAML_SEPARATOR
from . import ATTRIBUTE_INDENT
from . import ENTITY_INDENT
from . import GENERATED_EXTERNAL_TLS_CERTS_DIR
from . import MOUNTED_EXTERNAL_TLS_CERTS_DIR


ROUTER_iMAGE = "quay.io/interconnectedcloud/qdrouterd"

class Network(object):
    def __init__(self, routers=None, connectors=None, console_routes=None, yaml_output_dir=None):
        self.routers = routers
        self.connectors = connectors
        self.listener = None
        self.console_routes = console_routes
        self.yaml_output_dir = yaml_output_dir
        if not self.yaml_output_dir.endswith("/"):
            self.yaml_output_dir = self.yaml_output_dir + "/"

    def router_file_name(self, router_id):
        return router_id + ".conf"

    def router_yaml_file_name(self, router_id):
        return router_id + ".yaml"

    def find_to_connector(self, router_id):
        if not self.connectors:
            return None
        for connector in self.connectors:
            if connector.to_router == router_id:
                return connector
        return None

    def find_from_console_routes(self, router_id):
        if not self.console_routes:
            return None
        for console_route in self.console_routes:
            if console_route.router_id == router_id:
                return console_route
        return None


    def find_from_connectors(self, router_id):
        if not self.connectors:
            return None
        conns = []
        for connector in self.connectors:
            if connector.from_router == router_id:
                conns.append(connector)
        return conns

    def find_router_by_id(self, router_id):
        maching_router = None
        for router in self.routers:
            if router.id == router_id:
                maching_router = router
                break
        return maching_router

    def write_listeners(self, out):
        """
        Writes out listerns on ports amqp and 8672 (http)
        :param out:
        :return:
        """
        out.write("\n")
        # A default listener on port amqp for every router

        listeners = []

        listener = ListenerEntity()
        listener.defaults()
        listeners.append(listener)

        # A HTTP listener for all routers
        listener = ListenerEntity()
        listener.http_defaults()
        listeners.append(listener)

        # An edge listener for all routers
        listener = ListenerEntity()
        listener.edge_defaults()
        listeners.append(listener)

        # Skupper amqps listener
        listener = ListenerEntity()
        listener.skupper_amqps_defaults()
        listeners.append(listener)

        for listener in listeners:
            out.write(listener.to_string())
            out.write("\n")

    def generate_router_configs(self):
        # Kick off the script that creates the certificate authority
        p = subprocess.Popen(["../../certs/gen-ca-cert.sh", GENERATED_INTERNAL_TLS_CERTS_DIR], stdout=PIPE, universal_newlines=True)
        out = p.communicate()[0]

        p = subprocess.Popen(["../../certs/gen-ca-cert.sh", GENERATED_EXTERNAL_TLS_CERTS_DIR], stdout=PIPE, universal_newlines=True)
        out = p.communicate()[0]

        # contents of the file will be erased.
        if not os.path.exists(GENERATED_CONFIG_DIR):
            try:
                shutil.rmtree(GENERATED_CONFIG_DIR)
            except:
                pass
            os.makedirs(GENERATED_CONFIG_DIR)
        else:
            try:
                shutil.rmtree(GENERATED_CONFIG_DIR)
                os.makedirs(GENERATED_CONFIG_DIR)
            except OSError as e:
                print (e)
                os.makedirs(GENERATED_CONFIG_DIR)

        for router in self.routers:
            file_name = self.router_file_name(router.id)

            p = subprocess.Popen(["../../certs/gen-certs.sh",
                                  GENERATED_INTERNAL_TLS_CERTS_DIR,
                                  router.id.lower()],
                                 stdout=PIPE,
                                 universal_newlines=True)
            out = p.communicate()[0]

            p1 = subprocess.Popen(["../../certs/gen-certs.sh",
                                  GENERATED_EXTERNAL_TLS_CERTS_DIR,
                                  router.id.lower()],
                                 stdout=PIPE,
                                 universal_newlines=True)

            out = p1.communicate()[0]

            router_config_file = GENERATED_CONFIG_DIR + file_name
            with open(router_config_file, "w") as out:
                out.write(router.to_string())
                out.write("\n")

                for ssl_profile in router.sslProfiles:
                    out.write(ssl_profile.to_string())
                    ssl_profile.gen_base64_content()

                # Write default
                self.write_listeners(out)

                #Connectors
                connectors = self.find_from_connectors(router.id)
                # Each router gets one listener
                if self.listener:
                    out.write(self.listener.to_string())
                if connectors:
                    for conn in connectors:
                        out.write("\n")
                        to_router = self.find_router_by_id(conn.to_router)
                        from_router = self.find_router_by_id(conn.from_router)
                        if from_router and from_router.mode == "edge":
                            conn.role = "edge"
                        conn.host = to_router.host
                        out.write(conn.to_string())

                connector = self.find_to_connector(router.id)
                if connector:
                    if connector.to_router == router.id:
                        router.has_route = True
                        listener_attrs = {'host': '0.0.0.0', "port": "55671", "role": "inter-router", "saslMechanisms": "EXTERNAL", "authenticatePeer": "yes", 'sslProfile': 'skupper-internal'}

                        from_router = self.find_router_by_id(connector.from_router)
                        if from_router and from_router.mode == "edge":
                            listener_attrs['role'] = "edge"

                        listener = ListenerEntity(listener_attrs)
                        out.write("\n")
                        out.write(listener.to_string())

                # Write out the boiler pl;plate addresses
                out.write("\n")
                out.write("\n" + ENTITY_INDENT +  "address {\n"  + ATTRIBUTE_INDENT + "prefix: closest\n" + ATTRIBUTE_INDENT + "distribution: closest\n" + ENTITY_INDENT +  "} \n\n" + ENTITY_INDENT + "address {\n" + ATTRIBUTE_INDENT + "prefix: multicast\n" + ATTRIBUTE_INDENT + "distribution: multicast\n" + ENTITY_INDENT + "}\n")


        if not os.path.exists(self.yaml_output_dir):
            os.makedirs(self.yaml_output_dir)
        else:
            try:
                shutil.rmtree(self.yaml_output_dir)
                os.makedirs(self.yaml_output_dir)
            except OSError as e:
                os.makedirs(self.yaml_output_dir)

        for router in self.routers:
            # Now all the router related certs and config files have been created. Create the YAML file for each router

            yaml_file_name = self.yaml_output_dir + self.router_yaml_file_name(router.id)

            print ("yaml_file_name", yaml_file_name)

            with open(yaml_file_name, "w") as yamlout:

                # 1. Create deployments. Start with the skupper-router deployment
                with open("../../yaml/deployments/skupper-router.yaml", "r") as skupper_router_yaml:
                    content = skupper_router_yaml.read()
                    router_image = os.environ.get('QDROUTERD_IMAGE')
                    if not router_image:
                        router_image = ROUTER_iMAGE
                    file_name = self.router_file_name(router.id)
                    with open(GENERATED_CONFIG_DIR + file_name, "r") as router_config_file:
                        router_config  = router_config_file.read()
                        content = content %  (router_config, router_image)
                        yamlout.write(content)

                # Next deployment is skupper-proxy-contoller
                with open("../../yaml/deployments/skupper-proxy-controller.yaml", "r") as skupper_pc_yaml:
                    content = skupper_pc_yaml.read()
                    random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(15)])
                    content = content % (random_string)
                    yamlout.write(content)

                # skupper-internal secret
                with open("../../yaml/secrets/skupper-internal.yaml", "r") as secretsyaml:
                    content = secretsyaml.read()
                    ssl_profile = router.find_ssl_profile_by_name("skupper-internal")
                    content  = content % (ssl_profile.base64_cert, ssl_profile.base64_key, ssl_profile.base64_ca_cert)
                    yamlout.write(content)

                with open("../../yaml/secrets/skupper-amqps.yaml", "r") as secretsyaml:
                    content = secretsyaml.read()
                    ssl_profile = router.find_ssl_profile_by_name("skupper-amqps")
                    content  = content % (ssl_profile.base64_cert, ssl_profile.base64_key, ssl_profile.base64_ca_cert)
                    yamlout.write(content)

                with open("../../yaml/secrets/skupper.yaml", "r") as secretsyaml:
                    content = secretsyaml.read()
                    connect_string = {
                                       "scheme": "amqps",
                                        "verify": "false",
                                       "host": "skupper-messaging",
                                       "port": "5671",
                                        "tls": {
                                            "ca": "/etc/messaging/ca.crt",
                                            "cert": "/etc/messaging/tls.crt",
                                            "key": "/etc/messaging/tls.key",
                                            "verify": "false"
                                        }
                                  }
                    connect_json = json.dumps(connect_string)
                    connect_json_base64 = base64.b64encode(connect_json.encode()).decode('utf-8')
                    ssl_profile = router.find_ssl_profile_by_name("skupper-amqps")
                    content  = content % (ssl_profile.base64_ca_cert, ssl_profile.base64_cert, ssl_profile.base64_key, connect_json_base64)
                    yamlout.write(content)

                with open("../../yaml/secrets/skupper-ca.yaml", "r") as secretsyaml:
                    content = secretsyaml.read()
                    ssl_profile = router.find_ssl_profile_by_name("skupper-internal")
                    content  = content % (ssl_profile.base64_ca_cert, ssl_profile.base64_key)
                    yamlout.write(content)

                # roles
                with open("../../yaml/roles/skupper-edit.yaml", "r") as skupper_edit_yaml:
                    content = skupper_edit_yaml.read()
                    yamlout.write(content)

                with open("../../yaml/roles/skupper-view.yaml", "r") as skupper_view_yaml:
                    content = skupper_view_yaml.read()
                    yamlout.write(content)

                # role bindings
                with open("../../yaml/rolebindings/skupper-edit.yaml", "r") as skupper_edit_yaml:
                    content = skupper_edit_yaml.read()
                    yamlout.write(content)

                with open("../../yaml/rolebindings/skupper-view.yaml", "r") as skupper_view_yaml:
                    content = skupper_view_yaml.read()
                    yamlout.write(content)

                # Services
                with open("../../yaml/services/skupper-messaging.yaml", "r") as skupper_messaging_yaml:
                    content = skupper_messaging_yaml.read()
                    yamlout.write(content)

                with open("../../yaml/services/skupper-internal.yaml", "r") as skupper_internal_yaml:
                    content = skupper_internal_yaml.read()
                    yamlout.write(content)

                # ServiceAccounts
                with open("../../yaml/serviceaccounts/skupper-router.yaml", "r") as skupper_router_yaml:
                    content = skupper_router_yaml.read()
                    yamlout.write(content)

                with open("../../yaml/serviceaccounts/skupper-proxy-controller.yaml", "r") as skupper_proxy_yaml:
                    content = skupper_proxy_yaml.read()
                    yamlout.write(content)


                # Routes
                with open("../../yaml/routes/skupper-edge.yaml", "r") as skupper_edge_yaml:
                    content = skupper_edge_yaml.read()
                    try:
                        host = router.host
                        if host.find("inter-router") != -1:
                            host = host.replace("inter-router", "edge")
                            content  = content % host
                            yamlout.write(content)
                    except:

                        pass

                with open("../../yaml/routes/skupper-inter-router.yaml", "r") as skupper_ir_yaml:
                    content = skupper_ir_yaml.read()
                    content  = content % (router.host)
                    yamlout.write(content)











