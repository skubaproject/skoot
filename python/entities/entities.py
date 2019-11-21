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

import sys
import base64
from . import GENERATED_INTERNAL_TLS_CERTS_DIR
from . import MOUNTED_INTERNAL_TLS_CERTS_DIR
from . import ATTRIBUTE_INDENT
from . import ENTITY_INDENT

if sys.version_info[0] > 2:
    # Python 3 does not have a unicode() builtin method,
    # luckily all strings are unicode to start with
    def unicode(s):
        return s
    def dict_iteritems(d):
        return iter(d.items())
else:
    def dict_iteritems(d):
        return d.iteritems()

class BaseEntity(object):
    def __init__(self, attributes=None, **kwargs):
        self.__dict__['attributes'] = {}
        if attributes:
            for k, v in dict_iteritems(attributes):
                self.attributes[k] = v
                self.__dict__[self._pyname(k)] = v
        for k, v in dict_iteritems(kwargs):
            self._set(k, v)

    def __getitem__(self, name):
        return self.attributes[name]

    def __getattr__(self, name):
        return self.attributes[name]

    def __contains__(self, name):
        return name in self.attributes

    @staticmethod
    def _pyname(name): return name.replace('-', '_')

    def _set(self, name, value):
        """Subclasses can override _set to do validation on each change"""
        self.attributes[name] = value
        self.__dict__[self._pyname(name)] = value

    # Access using []
    def __setitem__(self, name, value): self._set(name, value)

    def __delitem__(self, name):
        del self.attributes[name]
        del self.__dict__[self._pyname(name)]

    # Access as python attribute.
    def __setattr__(self, name, value): self._set(name, value)

    def __delattr__(self, name):
        self.__delitem__(name)

    def __repr__(self): return "BaseEntity(%r)" % self.attributes


class ListenerEntity(BaseEntity):
    def __init__(self, attributes=None, **kwattrs):
        super(ListenerEntity, self).__init__(attributes, **kwattrs)

    def defaults(self):
        self.port = "5672"
        self.host = "0.0.0.0"
        self.role = "normal"
        self.sslProfile = None
        self.saslMechanisms = "ANONYMOUS"
        self.authenticatePeer = "no"

    def http_defaults(self):
        self.defaults()
        self.port = "9090"
        self.http = "yes"
        self.sslProfile = None
        self.httpRootDir = "disabled"
        self.healthz = "yes"
        self.metrics = "yes"
        self.websockets = "no"

    def edge_defaults(self):
        self.role = "edge"
        self.host = "0.0.0.0"
        self.port = "45671"
        self.sslProfile = "skupper-internal"
        self.saslMechanisms = "EXTERNAL"
        self.authenticatePeer = "no"

    def skupper_amqps_defaults(self):
        self.host = "0.0.0.0"
        self.sslProfile = "skupper-amqps"
        self.port = "5671"
        self.role = "normal"
        self.saslMechanisms = "EXTERNAL"
        self.authenticatePeer = "yes"

    def to_string(self):
        try:
            return ("\n" + ENTITY_INDENT + "listener {\n" + ATTRIBUTE_INDENT + "role: %s\n" + ATTRIBUTE_INDENT + "host: %s\n" + ATTRIBUTE_INDENT + "port: %s\n" + ATTRIBUTE_INDENT + "saslMechanisms: %s\n" + ATTRIBUTE_INDENT + "authenticatePeer:%s\n" + ATTRIBUTE_INDENT + "http: %s\n" + ATTRIBUTE_INDENT + "healthz: %s\n" + ATTRIBUTE_INDENT + "metrics: %s\n" + ATTRIBUTE_INDENT + "httpRootDir: %s\n" + ATTRIBUTE_INDENT + "websockets: %s\n" + ENTITY_INDENT + "}") % \
                   (self.role, self.host, self.port, self.saslMechanisms, self.authenticatePeer, self.http, self.healthz, self.metrics, self.httpRootDir, self.websockets)
        except:
            if self.sslProfile:
                return ("\n" + ENTITY_INDENT + "listener {\n" + ATTRIBUTE_INDENT + "sslProfile: %s\n" + ATTRIBUTE_INDENT + "role: %s\n" + ATTRIBUTE_INDENT + "host: %s\n" + ATTRIBUTE_INDENT + "port: %s\n" + ATTRIBUTE_INDENT + "saslMechanisms: %s\n" + ATTRIBUTE_INDENT + "authenticatePeer:%s\n" + ENTITY_INDENT + "}") % \
                       (self.sslProfile, self.role, self.host, self.port, self.saslMechanisms, self.authenticatePeer)
            else:
                return ("\n" + ENTITY_INDENT + "listener {\n" + ATTRIBUTE_INDENT + "role: %s\n" + ATTRIBUTE_INDENT + "host: %s\n" + ATTRIBUTE_INDENT + "port: %s\n" + ATTRIBUTE_INDENT + "saslMechanisms: %s\n" + ATTRIBUTE_INDENT + "authenticatePeer:%s\n" + ENTITY_INDENT + "}") % \
                       (self.role, self.host, self.port, self.saslMechanisms, self.authenticatePeer)


class ConnectorEntity(BaseEntity):
    def __init__(self, from_router=None, to_router=None, attributes=None, **kwattrs):
        super(ConnectorEntity, self).__init__(attributes, **kwattrs)
        self.from_router = from_router
        self.to_router = to_router

    def to_string(self):
        ret_val = ("\n" + ENTITY_INDENT + "connector {\n" + ATTRIBUTE_INDENT + "name: to_%s\n" + ATTRIBUTE_INDENT + "host: %s\n" + ATTRIBUTE_INDENT + "port: %s\n" + ATTRIBUTE_INDENT + "saslMechanisms: %s\n" + ATTRIBUTE_INDENT + "sslProfile: %s\n" + ATTRIBUTE_INDENT + "verifyHostname: %s\n" + ATTRIBUTE_INDENT + "role: %s\n"  ) % (self.to_router, self.host, self.port, self.saslMechanisms, self.sslProfile, self.verifyHostname, self.role)
        try:
            if self.cost:
                ret_val = ret_val  + ATTRIBUTE_INDENT +  'cost: ' + self.cost + "\n"
        except:
            pass

        ret_val = ret_val  + ENTITY_INDENT +  '}'
        return ret_val


class RouterEntity(BaseEntity):
    def __init__(self, attributes=None, **kwattrs):
        super(RouterEntity, self).__init__(attributes, **kwattrs)
        self.has_route = False

    def find_ssl_profile_by_name(self, name):
        for ssl_profile in self.sslProfiles:
            if ssl_profile.name == name:
                return ssl_profile

    def to_string(self):
        return (ENTITY_INDENT + "router {\n" + ATTRIBUTE_INDENT + "id:%s\n" + ATTRIBUTE_INDENT + "mode: %s\n" + ENTITY_INDENT + "}") % (self.id, self.mode)

class SslProfileEntity(BaseEntity):
    def __init__(self, attributes=None, tls_cert_dir=GENERATED_INTERNAL_TLS_CERTS_DIR, mounted_cert_dir=MOUNTED_INTERNAL_TLS_CERTS_DIR, **kwattrs):
        super(SslProfileEntity, self).__init__(attributes, **kwattrs)
        self.cert_file = tls_cert_dir + "tls." + self.router_id + ".crt"
        self.key_File = tls_cert_dir + "tls." + self.router_id + ".key"
        self.ca_certFile = tls_cert_dir + "ca.crt"

        self.mounted_cert_file = mounted_cert_dir + "tls.crt"
        self.mounted_key_File = mounted_cert_dir + "tls.key"
        self.mounted_ca_certFile = mounted_cert_dir + "ca.crt"

    def gen_base64_content(self):
        with open(self.cert_file, "r") as certfile:
            content = certfile.read()
            self.base64_cert =  base64.b64encode(content.encode()).decode('utf-8')

        with open(self.key_File, "r") as keyfile:
            content = keyfile.read()
            self.base64_key =  base64.b64encode(content.encode()).decode('utf-8')

        with open(self.ca_certFile, "r") as cacertfile:
            content = cacertfile.read()
            self.base64_ca_cert =  base64.b64encode(content.encode()).decode('utf-8')

    def to_string(self):
        return ("\n" + ENTITY_INDENT + "sslProfile {\n" + ATTRIBUTE_INDENT + "name:%s\n" + ATTRIBUTE_INDENT + "certFile: %s\n" + ATTRIBUTE_INDENT + "keyFile:%s\n" + ATTRIBUTE_INDENT +   "caCertFile: %s\n" +  ENTITY_INDENT +  "}") % (self.name, self.mounted_cert_file, self.mounted_key_File, self.mounted_ca_certFile)


class ConsoleRouteEntity(BaseEntity):
    def __init__(self, attributes=None, **kwattrs):
        super(ConsoleRouteEntity, self).__init__(attributes, **kwattrs)
