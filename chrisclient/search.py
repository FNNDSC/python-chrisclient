#!/usr/bin/env python3

import  logging
logging.disable(logging.CRITICAL)

import  os
import  sys
import  json
import  socket
import  requests
import  ast
import  pudb

import  pfmisc

# pfstorage local dependencies
from    pfmisc._colors      import  Colors
from    pfmisc.debug        import  debug
from    pfmisc.C_snode      import  *
from    pfstate             import  S

class D(S):
    """
    A derived 'pfstate' class that keeps system state.

    See https://github.com/FNNDSC/pfstate for more information.
    """

    def __init__(self, *args, **kwargs):
        """
        An object to hold some generic/global-ish system state, in C_snode
        trees.
        """
        d_sysArgs   : dict      = {}
        d_CUBE      : dict      = {
                "protocol":     "http",
                "port":         "8000",
                "address":      "%HOSTIP",
                "user":         "chris",
                "password":     "chris1234",
        }
        for k,v in kwargs.items():
            if k == 'args': d_sysArgs   = v
        if len(d_sysArgs['str_CUBE']):
            d_CUBE  = ast.literal_eval("".join(d_sysArgs['str_CUBE'].split()))
        self.state_create(
        {
            "CUBE": d_CUBE,
            "self":
            {
                'httpProxy':
                {
                    'use':      False,
                    'httpSpec': ''
                }
            },
            "this":
            {
                'verbosity':    0,
                'colorize':     False
            }
        },
        *args, **kwargs)

class PluginSearch(object):
    """
    A class that interacts with CUBE via the collection+json API
    and is specialized to perform searches on the plugin space.
    """

    def S(self, *args):
        """
        set/get components of the state object
        """
        if len(args) == 1:
            return self.state.T.cat(args[0])
        else:
            self.state.T.touch(args[0], args[1])

    def __init__(self, d_meta, *args, **kwargs):
        """
        Class constructor.
        """
        self.d_args     = vars(*args)
        self.state      = D(
            version     = d_meta['version'],
            name        = d_meta['name'],
            desc        = d_meta['desc'],
            args        = vars(*args)
        )
        self.dp         = pfmisc.debug(
            verbosity   = int(self.d_args['verbosity']),
            within      = d_meta['name'],
            syslog      = self.d_args['b_syslog'],
            colorize    = self.state.T.cat('/this/colorize')
        )
        # Check the IP in the state structure and optionally update
        IP = self.S('/CUBE/address')
        if IP == "%HOSTIP":
            self.S('/CUBE/address', d_meta['defIP'])

    def search_templatize(self):
        """
        Parse the CLI '--using <template>' and return a dictionary
        of parameters to search.

        The <template> value is of form:

            name_exact=<name>,version=<version>,[<key>=<value>,...]

        and is returned as

            {
                'name_exact':   <name>,
                'version':      <version>[,
                <key>:          <value>]
            }

        """
        b_status    : bool      = False
        d_params    : dict      = {}
        str_message : str       = ''
        paramCount  : int       = 0

        if 'str_using' in self.d_args.keys():
            if len(self.d_args['str_using']):
                l_using     = self.d_args['str_using'].split(',')
                for param in l_using:
                    l_keyVal    = param.split('=')
                    d_params[l_keyVal[0]]   = l_keyVal[1]
                    paramCount += 1
                    b_status    = True
                str_message = '%d parameters templatized' % paramCount
            else:
                str_message = "'--using' value is zero length"
        else:
            str_message     = "'--using' not in CLI args"

        return {
            'status':   b_status,
            'message':  str_message,
            'params':   d_params
        }

    def search_CUBEAPIcall(self):
        """

        This method implements the actual search logic.

        """
        d_resp              : dict  = {}
        d_templatize        : dict  = self.search_templatize()
        b_status            : bool  = False
        str_message         : str   = 'CUBE API not called because of previous error'
        if d_templatize['status']:
            d_params    = d_templatize['params']
            d_headers           : dict = {
                'Accept':   'application/vnd.collection+json'
            }
            d_resp              : dict = {}
            str_dataServiceAddr : str  = "%s://%s:%s" % (
                                    self.S('/CUBE/protocol'),
                                    self.S('/CUBE/address'),
                                    self.S('/CUBE/port')
                                )
            str_dataServiceURL  : str  = 'api/v1/%s/search/?limit=100' % \
                                            self.d_args['str_searchURL']
            str_user            : str  = self.S('/CUBE/user')
            str_passwd          : str  = self.S('/CUBE/password')
            str_URL             : str  = '%s/%s' % (
                                    str_dataServiceAddr,
                                    str_dataServiceURL
                                )
            try:
                resp = requests.get(
                                    str_URL,
                                    params  = d_params,
                                    auth    = (str_user, str_passwd),
                                    timeout = 30,
                                    headers = d_headers
                        )
                b_status        = True
                str_message     = "CUBE call return a response"
            except (requests.exceptions.Timeout,
                    requests.exceptions.RequestException) as e:
                logging.error(str(e))
                str_message     = "CUBE call return some error"
                raise
            d_resp = resp.json()
        return {
            'status':       b_status,
            'templatize':   d_templatize,
            'response':     d_resp,
            'message':      str_message
        }

    def search_desiredReturnFind(self, d_search):
        """
        For a given search response from CUBE, return the
        specific value sought.
        """
        b_status        :   bool    = False
        l_thistarget    :   list    = []
        l_target        :   list    = []
        str_message     :   str     = 'search returned no response'
        b_keysListed    :   bool    = False
        l_keys          :   list    = []

        if d_search['status']:
            if d_search['response']['collection']['total']:
                for d_hit in d_search['response']['collection']['items']:
                    l_data  :   list = d_hit['data']
                    if not b_keysListed:
                        for d_el in l_data:
                            l_keys.append(d_el['name'])
                        b_keysListed = True
                    l_thistarget     = []
                    for str_desired in self.d_args['str_for'].split(','):
                        l_hit   :   list = list(
                                    filter(
                                        lambda info: info['name'] == str_desired, l_data
                                        )
                                    )
                        if len(l_hit):
                            l_thistarget.append(l_hit[0])
                            b_status    = True
                    l_target.append(l_thistarget)

        if not len(l_target):
            str_message     = "No targets found"
        else:
            str_message     = "%s target(s) found" % len(l_target)

        return {
            'status':   b_status,
            'search':   d_search,
            'target':   l_target,
            'message':  str_message,
            'keys':     l_keys
        }

    def do(self):
        """
        Main entry point to this class.
        """
        d_result    = self.search_desiredReturnFind(self.search_CUBEAPIcall())
        return d_result
