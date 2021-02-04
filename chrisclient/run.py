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
from    chrisclient         import  search
from    argparse            import  Namespace

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
        if len(d_sysArgs['str_CUBEaddress']):
            d_CUBE['address']   = d_sysArgs['str_CUBEaddress']
        if len(d_sysArgs['str_CUBEport']):
            d_CUBE['port']      = d_sysArgs['str_CUBEport']
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

class PluginRun(object):
    """
    A class that interacts with CUBE via the collection+json API
    and is specialized to "run" a plugin via POST requests to the
    backend.
    """

    def S(self, *args):
        """
        set/get components of the state object
        """
        if len(args) == 1:
            return self.state.T.cat(args[0])
        else:
            self.state.T.touch(args[0], args[1])

    def CUBE_IPspec(self):
        """
        Check and update the %HOSTIP if required
        """

        IP = self.S('/CUBE/address')
        if IP == "%HOSTIP":
            self.S('/CUBE/address', self.d_meta['defIP'])

    def __init__(self, d_meta, *args, **kwargs):
        """
        Class constructor.
        """

        # Structures to contain the "CLI" of the plugin
        # to be scheduled/run
        self.d_args         : dict  = vars(*args)
        self.d_CLIargs      : dict  = {}
        self.d_CLIvals      : dict  = {}
        self.d_CLItemplate  : dict  = {}

        # Some additional "massaging" from these CLI
        # to CLI appropriate for the search module:
        self.d_args['str_using']    = self.d_args['str_pluginSpec']
        self.d_args['str_for']      = 'id'
        ns                          = Namespace(**self.d_args)

        # The search module -- used to determine the plugin ID
        # in ChRIS/CUBE
        self.query                  = search.PluginSearch(d_meta, ns)
        self.str_pluginID   : str   = ''

        # Generic "state" data, mostly describing the
        # compute environment in which CUBE exists
        self.d_meta     = d_meta
        self.state      = D(
            version     = d_meta['version'],
            name        = d_meta['name'],
            desc        = d_meta['desc'],
            args        = vars(*args)
        )

        # A debug/print object
        self.dp         = pfmisc.debug(
            verbosity   = int(self.d_args['verbosity']),
            within      = d_meta['name'],
            syslog      = self.d_args['b_syslog'],
            colorize    = self.state.T.cat('/this/colorize')
        )

        # Quick housekeeping
        self.CUBE_IPspec()

    def pluginCLIargs_parse(self):
        """
        Parse the string of CLI args into a dictionary
        structure.
        """
        l_args      :   list    = []
        l_keyval    :   list    = []
        b_add       :   bool    = True
        str_message :   str     = "'--args' is empty!"

        if len(self.d_args['str_args']):
            l_args  = self.d_args['str_args'].split(';')
            for str_keyval in l_args:
                l_keyval    = str_keyval.split('=')
                if len(l_keyval) == 1:
                    key         = l_keyval[0]
                    val         = True
                if len(l_keyval) == 2:
                    (key, val)  = l_keyval
                    val         = val.rstrip('"-=')
                if b_add:
                    # For the set [ " - = ], remove any leading/
                    # trailing hits in the <key> as well as any
                    # trailing hits in the <val>.
                    key         = "".join(key.split())
                    key         = key.strip('"-=')
                    self.d_CLIargs.update({key: val})
        if b_add:
            str_message     = '%d args parsed' % len(l_args)
        return {
            'status':   b_add,
            'message':  str_message,
            'CLIdict':  self.d_CLIargs
        }

    def pluginArgs_CLIvalsFind(self):
        """
        The plugin has a pattern of CLI flags. These flags are associated
        with a variable inside the plugin argparse code. CUBE requires that
        args are POSTed to this variable name, NOT the CLI string.

        This method finds, for each CLI flag, the corresponding value and
        saves this in self.d_CLIvals, key indexed by the name to POST and
        the CLI value.

        Some exceptions to the CLI / name lookup can be defined. These
        are not subject to the indirect value calculation but are passed
        directly to CUBE. Typical exceptions include '--previous_id' and
        '--title'.
        """

        b_status    : bool          = False
        l_hits      : list          = []
        l_directArg : list          = []
        d_val       : dict          = {}
        d_query     : dict          = {}
        d_search    : dict          = {
            'str_for':          'flag,name',
            'str_using':        'plugin_id=%s' % self.str_pluginID,
            'str_across':       'parameters',
            'str_CUBE':         self.d_args['str_CUBE'],
            'str_filterFor':    'key'
        }
        l_directArg = ["previous_id", "title"]
        for key in self.d_CLIargs:
            b_status                        = True
            if key not in l_directArg:
                d_search['str_filterFor']   = '--' + key
                ns                          = Namespace(**d_search)
                self.query                  = search.PluginSearch(self.d_meta, ns)
                d_query                     = self.query.do()
                if len(d_query['target']):
                    l_hits                  = d_query['target'][0]
                    str_userCLIvalue        = self.d_CLIargs[key]
                    d_val = next((el for el in l_hits if el['name'] == 'name'))
                    self.d_CLIvals[d_val['value']] = str_userCLIvalue
            if key in l_directArg:
                self.d_CLIvals[key] = self.d_CLIargs[key]
            # if key == 'previous_id':
            #     self.d_CLIvals['previous_id'] = self.d_CLIargs['previous_id']
        return {
            'status':           b_status,
            'CUBEpluginVals':   self.d_CLIvals
        }

    def pluginArgs_templateCreate(self, d_argsParse):
        """
        Create a collectio+json template from the intenal
        plugin argument dictionary
        """
        b_status            : bool  = True
        d_CUBEpluginVals    : dict  = {}
        self.d_CLItemplate  = {'data' : []}
        str_message         : str   = 'template creation failed due to earlier error'
        keyCount            : int   = 0

        if d_argsParse['status']:
            d_CUBEpluginVals = self.pluginArgs_CLIvalsFind()
            if d_CUBEpluginVals['status']:
                for key in self.d_CLIvals:
                    self.d_CLItemplate['data'].append(
                        {
                            'name':     key,
                            'value':    self.d_CLIvals[key]
                        }
                    )
                    keyCount += 1
        if d_CUBEpluginVals['status']:
            str_message     = '%s key(s) parsed into template' % keyCount
        else:
            str_message     = 'Finding match between CLI flags and CUBE variables failed.'
        return {
            'status':       d_CUBEpluginVals['status'],
            'message':      str_message,
            'template':     self.d_CLItemplate,
            'argsParse':    d_argsParse
        }

    def pluginRun_CUBEAPIcall(self, d_templatize):
        """

        This method POSTs the call to the CUBE API to perform
        the actual plugin execution.

        """
        d_resp              : dict  = {}
        b_status            : bool  = False
        str_message         : str   = 'CUBE API not called because of earlier error'

        if d_templatize['status']:
            d_headers           : dict = {
                'Accept':       'application/vnd.collection+json',
                'Content-Type': 'application/vnd.collection+json'
            }
            str_dataServiceAddr : str  = "%s://%s:%s" % (
                                    self.S('/CUBE/protocol'),
                                    self.S('/CUBE/address'),
                                    self.S('/CUBE/port')
                                )
            str_dataServiceURL  : str  = 'api/v1/plugins/%s/instances/' % \
                                    self.str_pluginID
            str_user            : str  = self.S('/CUBE/user')
            str_passwd          : str  = self.S('/CUBE/password')
            str_URL             : str  = '%s/%s' % (
                                    str_dataServiceAddr,
                                    str_dataServiceURL
                                )
            try:
                resp = requests.post(
                                    str_URL,
                                    data    = json.dumps(
                                        {'template' : self.d_CLItemplate}
                                    ),
                                    auth    = (str_user, str_passwd),
                                    timeout = 30,
                                    headers = d_headers
                        )
                b_status    = True
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

    def pluginInstanceID_find(self, d_run):
        """
        Once a job has been POSTed, parse the return from
        CUBE for the plugin instance ID.
        """
        b_status        :   bool    = False
        l_thistarget    :   list    = []
        l_target        :   list    = []
        str_message     :   str     = 'No instance ID found due to earlier error'

        if d_run['status']:
            if 'error' in d_run['response']['collection'].keys():
                str_message = d_run['response']['collection']['error']['message']
            if 'items' in d_run['response']['collection'].keys():
                for d_hit in d_run['response']['collection']['items']:
                    l_data  :   list = d_hit['data']
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
                str_message     = '%d instance ID(s) found' % len(l_target)
        return {
            'status':   b_status,
            'run':      d_run,
            'target':   l_target,
            'message':  str_message
        }

    def do(self):
        """
        Main entry point to this class.
        """
        b_status    :   bool    = False
        str_message :   str     = ''
        d_query     :   dict    = {}
        d_targetID  :   dict    = {}
        d_run       :   dict    = {}

        # First, find the plugin ID for the desired plugin
        # to run
        d_query             = self.query.do()
        if len(d_query['target']) == 1:
            d_targetID          = d_query['target'][0][0]
            self.str_pluginID   = d_targetID['value']

            # and now, run it!
            d_run:  dict    = self.pluginInstanceID_find(
                                self.pluginRun_CUBEAPIcall(
                                    self.pluginArgs_templateCreate(
                                        self.pluginCLIargs_parse()
                                    )
                                )
                            )
            if d_run['status']:
                str_message = 'plugin scheduled successfully'
                b_status    = True
            else:
                str_message = 'plugin run NOT scheduled'
        else:
            str_message     = "plugin query MUST return a single hit"
        return {
            'status':       b_status,
            'query':        d_query,
            'run':          d_run,
            'message':      str_message
        }


