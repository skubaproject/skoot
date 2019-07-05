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
    """
    A collection of named attributes.

    Attribute access:
    - via index operator: entity['foo']
    - as python attributes: entity.foo (only if attribute name is a legal python identitfier
      after replacing '-' with '_')

    @ivar attributes: Map of attribute values for this entity.

    NOTE: BaseEntity does not itself implement the python map protocol because map
    methods (in particular 'update') can clash with AMQP methods and attributes.
    """

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
        self.port = "amqp"
        self.host = "0.0.0.0"
        self.authenticatePeer = "no"
        self.saslMechanisms = "ANONYMOUS"
        self.role = "normal"

    def http_defaults(self):
        self.defaults()
        self.port = "8672"
        self.http = "yes"


    def to_string(self):
        try:
            return "\nlistener {\n   role: %s\n   host: %s\n   port: %s\n   saslMechanisms: %s\n   authenticatePeer:%s\n   http: %s\n}" % (self.role, self.host, self.port, self.saslMechanisms, self.authenticatePeer, self.http)
        except:
            return "\nlistener {\n   role: %s\n   host: %s\n   port: %s\n   saslMechanisms: %s\n   authenticatePeer:%s\n}" % (
            self.role, self.host, self.port, self.saslMechanisms,
            self.authenticatePeer)


class ConnectorEntity(BaseEntity):
    def __init__(self, from_router=None, to_router=None, attributes=None, **kwattrs):
        super(ConnectorEntity, self).__init__(attributes, **kwattrs)
        self.from_router = from_router
        self.to_router = to_router

    def to_string(self):
        #return "connector {\n name: %s\nrole: inter-router\n host: %s \n port: %s \nsaslMechanisms: EXTERNAL\n sslProfile: %s }" % self.to_router, self.host, self.port, self.ssl_profile
        return "\nconnector {\n   name: to_%s\n   host: %s\n   port: %s\n   saslMechanisms: %s\n   sslProfile: %s\n}" % (self.to_router, self.host, self.port, self.saslMechanisms, self.sslProfile)

class RouterEntity(BaseEntity):
    def __init__(self, attributes=None, **kwattrs):
        super(RouterEntity, self).__init__(attributes, **kwattrs)
        self.mode="interior"

    def to_string(self):
        return "router {\n   id:%s\n   mode: %s\n}" % (self.id, self.mode)

class SslProfileEntity(BaseEntity):
    def __init__(self, attributes=None, **kwattrs):
        super(SslProfileEntity, self).__init__(attributes, **kwattrs)
        self.mode="interior"

    def to_string(self):
        return "\nsslProfile {\n   name:%s\n   caCertFile: %s\n   certFile:%s\n   passwordFile: %s\n   certDb: %s\n}" % (self.name, self.ca_cert_file, self.cert_file, self.password_file, self.cert_db)
