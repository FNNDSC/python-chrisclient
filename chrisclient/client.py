"""
ChRIS API client module.
An item in a collection is represented by a dictionary. A collection of items is
represented by a list of dictionaries.
"""

from .request import Request
from .exceptions import ChrisRequestException
import json


class Client(object):
    """
    A ChRIS API client.
    """

    def __init__(self, url, username=None, password=None, token=None):
        self.url = url
        self.query_url_sufix = 'search/'
        self.content_type = 'application/vnd.collection+json'
        self.auth = None

        if (username is not None and password is None) or (
                username is None and password is not None):
            raise ValueError('Both username and password must be provided together.')

        if username is not None and password is not None:
            # username/password have priority
            self.auth = {'username': username, 'password': password}
        elif token is not None:
            self.auth = {'token': token}

        self._request = Request(self.auth, self.content_type)

        # urls of the high level API resources
        self.feeds_url = self.url
        self.public_feeds_url = ''
        self.chris_instance_url = ''
        self.compute_resources_url = ''
        self.plugin_metas_url = ''
        self.plugins_url = ''
        self.plugin_instances_url = ''
        self.pipelines_url = ''
        self.workflows_url = ''
        self.tags_url = ''
        self.pipeline_source_files_url = ''
        self.user_files_url = ''
        self.pacs_files_url = ''
        self.pacs_url = ''
        self.pacs_queries_url = ''
        self.pacs_series_url = ''
        self.file_browser_url = ''
        self.download_tokens_url = ''
        self.groups_url = ''
        self.user_url = ''
        self.admin_url = ''

    def set_urls(self, timeout=30):
        """
        Set the urls of the high level API resources.
        """
        get_url = Request.get_link_relation_urls

        req = self._request
        coll = req.get(self.url, None, timeout)

        # get urls of the high level API resources
        self.public_feeds_url = self.public_feeds_url or get_url(coll, 'public_feeds')[0]
        self.chris_instance_url = self.chris_instance_url or get_url(
            coll, 'chrisinstance')[0]
        self.compute_resources_url = self.compute_resources_url or get_url(
            coll, 'compute_resources')[0]
        self.plugin_metas_url = self.plugin_metas_url or get_url(coll, 'plugin_metas')[0]
        self.plugins_url = self.plugins_url or get_url(coll, 'plugins')[0]
        self.plugin_instances_url = self.plugin_instances_url or get_url(
            coll, 'plugin_instances')[0]
        self.pipelines_url = self.pipelines_url or get_url(coll, 'pipelines')[0]
        self.workflows_url = self.workflows_url or get_url(coll, 'workflows')[0]
        self.tags_url = self.tags_url or get_url(coll, 'tags')[0]
        self.pipeline_source_files_url = self.pipeline_source_files_url or get_url(
            coll, 'pipelinesourcefiles')[0]
        self.user_files_url = self.user_files_url or get_url(
            coll, 'userfiles')[0]
        self.pacs_files_url = self.pacs_files_url or get_url(coll, 'pacsfiles')[0]
        self.pacs_url = self.pacs_url or get_url(coll, 'pacs')[0]
        self.pacs_queries_url = self.pacs_queries_url or get_url(coll, 'pacsqueries')[0]
        self.pacs_series_url = self.pacs_series_url or get_url(coll, 'pacsseries')[0]
        self.file_browser_url = self.file_browser_url or get_url(coll, 'filebrowser')[0]

        if not self.download_tokens_url:
            urls = get_url(coll, 'download_tokens')
            self.download_tokens_url = urls[0] if urls else ''

        if not self.groups_url:
            urls = get_url(coll, 'groups')
            self.groups_url = urls[0] if urls else ''

        if not self.user_url:
            urls = get_url(coll, 'user')
            self.user_url = urls[0] if urls else ''

        if not self.admin_url:
            urls = get_url(coll, 'admin')
            self.admin_url = urls[0] if urls else ''

    def get_chris_instance(self, timeout=30):
        """
        Get a ChRIS's instance data (descriptors).
        """
        coll = self._fetch_resource('chris_instance_url', None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_feeds(self, search_params=None, timeout=30):
        """
        Get a paginated list of feeds (data descriptors) given query search parameters.
        If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('feeds_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_public_feeds(self, search_params=None, timeout=30):
        """
        Get a paginated list of public feeds (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('public_feeds_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_feed_by_id(self, id, timeout=30):
        """
        Get a feed's data (descriptors) given its ChRIS id.
        """
        result = self.get_feeds({'id': id}, timeout)

        if result['data']:
            return result['data'][0]  # resource-specific ids are unique
        raise ChrisRequestException(f'Could not find feed with id {id}')

    def get_plugins(self, search_params=None, timeout=30):
        """
        Get a paginated list of plugins (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('plugins_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_plugin_by_id(self, id, timeout=30):
        """
        Get a plugin's data (descriptors) given its ChRIS id.
        """
        result = self.get_plugins({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find plugin with id {id}')

    def get_plugin_parameters(self, plugin_id, params=None, timeout=30):
        """
        Get a plugin's paginated parameters given its ChRIS id.
        """
        coll = self._fetch_resource('plugins_url', {'id': plugin_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find plugin with id: {plugin_id}.')

        parameters_links = Request.get_link_relation_urls(coll.items[0], 'parameters')

        if parameters_links:
            req = self._request
            coll = req.get(parameters_links[0], params, timeout) # there can only be a single parameters link
            return Request.get_data_from_collection(coll)

        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def get_plugin_metas(self, search_params=None, timeout=30):
        """
        Get a paginated list of plugin metas (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('plugin_metas_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_plugin_meta_by_id(self, id, timeout=30):
        """
        Get a plugin meta's data (descriptors) given its ChRIS id.
        """
        result = self.get_plugin_metas({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find plugin meta with id {id}')

    def get_compute_resources(self, search_params=None, timeout=30):
        """
        Get a paginated list of compute resources (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('compute_resources_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_compute_resource_by_id(self, id, timeout=30):
        """
        Get a compute_resource's data (descriptors) given its ChRIS id.
        """
        result = self.get_compute_resources({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find compute resource with id {id}')

    def admin_upload_plugin(self, compute_names, data, timeout=30):
        """
        Upload a plugin representation file and create a new plugin. The data argument
        can be:
            * a string indicating a local file path, or
            * a file handler, or
            * a python dictionary representation.
        """
        if not self.admin_url: self.set_urls(timeout)
        if not self.admin_url:
            raise ChrisRequestException(f"User is not a ChRIS admin.")

        if isinstance(data, str):
            with open(data, 'rb') as f:
                file_contents = f.read()
        elif type(data) is dict:
            file_contents = json.dumps(data, indent = 4).encode('utf-8')
        else:
            file_contents = data.read()

        comp = {'compute_names': compute_names}

        req = self._request
        coll = req.post(self.admin_url, comp, file_contents, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def admin_register_plugin_with_computes(self, plugin_id, compute_names, timeout=30):
        """
        Register an existing plugin with a set of existing compute resources.
        """
        if not self.admin_url: self.set_urls(timeout)
        if not self.admin_url:
            raise ChrisRequestException(f"User is not a ChRIS admin.")

        data = {'compute_names': compute_names}

        req = self._request
        coll = req.put(self.admin_url + f'{plugin_id}/', data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_plugin_instances(self, search_params=None, timeout=30):
        """
        Get a paginated list of plugin instances (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('plugin_instances_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_plugin_instance_by_id(self, id, timeout=30):
        """
        Get a plugin instance's data (descriptors) given its ChRIS id.
        """
        result = self.get_plugin_instances({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find plugin instance with id {id}')

    def create_plugin_instance(self, plugin_id, data, timeout=30):
        """
        Create a plugin instance given the corresponding plugin id and plugin-specific
        data dictionary.
        """
        coll = self._fetch_resource('plugins_url', {'id': plugin_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find plugin with id: {plugin_id}.')

        instances_links = Request.get_link_relation_urls(coll.items[0], 'instances')

        req = self._request
        coll = req.post(instances_links[0], data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def create_plugin_instance_split(self, plg_inst_id, filter='', cr_name='', timeout=30):
        """
        Create a plugin instance given the corresponding plugin id and plugin-specific
        data dictionary.
        """
        coll = self._fetch_resource('plugin_instances_url', {'id': plg_inst_id},
                                    timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find plugin instance with id: {plg_inst_id}')

        splits_links = Request.get_link_relation_urls(coll.items[0], 'splits')

        data = {'filter': filter}
        if cr_name: data['compute_resource_name'] = cr_name

        req = self._request
        coll = req.post(splits_links[0], data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_pipelines(self, search_params=None, timeout=30):
        """
        Get a paginated list of pipelines (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('pipelines_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_pipeline_by_id(self, id, timeout=30):
        """
        Get a pipeline's data (descriptors) given its ChRIS id.
        """
        result = self.get_pipelines({'id': id}, timeout)

        if result['data']:
            return result['data'][0]  # pipeline ids are unique
        raise ChrisRequestException(f'Could not find pipeline with id {id}')

    def get_pipeline_default_parameters(self, pipeline_id, params=None, timeout=30):
        """
        Get a pipeline's paginated default parameters given its ChRIS id.
        """
        coll = self._fetch_resource('pipelines_url', {'id': pipeline_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find pipeline with id: '
                                        f'{pipeline_id}.')
        parameters_links = Request.get_link_relation_urls(coll.items[0],
                                                          'default_parameters')
        if parameters_links:
            req = self._request
            coll = req.get(parameters_links[0], params, timeout)
            return Request.get_data_from_collection(coll)
        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def create_pipeline(self, data, timeout=30):
        """
        Create a pipeline given the data dictionary.
        """
        if not self.pipelines_url: self.set_urls(timeout)

        req = self._request
        coll = req.post(self.pipelines_url, data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_workflows(self, search_params=None, timeout=30):
        """
        Get a paginated list of workflows (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('workflows_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_workflow_by_id(self, id, timeout=30):
        """
        Get a workflow's data (descriptors) given its ChRIS id.
        """
        result = self.get_workflows({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find workflow with id {id}')

    def get_workflow_plugin_instances(self, workflow_id, params=None, timeout=30):
        """
        Get a workflow's paginated list of plugin instances given its ChRIS id.
        """
        coll = self._fetch_resource('workflows_url', {'id': workflow_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find workflow with id: {workflow_id}.')

        parameters_links = Request.get_link_relation_urls(coll.items[0],
                                                          'plugin_instances')
        if parameters_links:
            req = self._request
            coll = req.get(parameters_links[0], params, timeout)
            return Request.get_data_from_collection(coll)
        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def create_workflow(self, pipeline_id, data, timeout=30):
        """
        Create a workflow given the corresponding pipeline id and pipeline-specific
        data dictionary.
        """
        coll = self._fetch_resource('pipelines_url', {'id': pipeline_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find pipeline with id: '
                                        f'{pipeline_id}.')

        workflows_links = Request.get_link_relation_urls(coll.items[0], 'workflows')

        req = self._request
        coll = req.post(workflows_links[0], data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def compute_workflow_nodes_info(self, pipeline_default_parameters,
                                    include_all_defaults=False):
        """
        Helper method to create the nodes_info data structure required to create a
        workflow from a pipeline's default parameters data returned by the
        get_pipeline_default_parameters. If include_all_defaults is set to True
        then non-null parameters are also included in the result.
        """
        pipings_dict = {}
        for default_param in pipeline_default_parameters:
            piping_id = default_param['plugin_piping_id']

            if piping_id not in pipings_dict:
                pipings_dict[piping_id] = {
                    'piping_id': piping_id,
                    'previous_piping_id': default_param['previous_plugin_piping_id'],
                    'compute_resource_name': 'host',
                    'title': default_param['plugin_piping_title'],
                    'plugin_parameter_defaults': []
                }

            if default_param['value'] is None or include_all_defaults:
                pipings_dict[piping_id]['plugin_parameter_defaults'].append(
                    {
                        'name': default_param['param_name'],
                        'default': default_param['value']
                    }
                )

        nodes_info = []
        for piping_id in pipings_dict:
            if not pipings_dict[piping_id]['plugin_parameter_defaults']:
                del pipings_dict[piping_id]['plugin_parameter_defaults']
            nodes_info.append(pipings_dict[piping_id])
        return nodes_info

    def get_tags(self, search_params=None, timeout=30):
        """
        Get a paginated list of tags (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('tags_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_tag_by_id(self, id, timeout=30):
        """
        Get a tag's data (descriptors) given its ChRIS id.
        """
        result = self.get_tags({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find tag with id {id}')

    def create_tag(self, data, timeout=30):
        """
        Create a tag given the data dictionary.
        """
        if not self.tags_url: self.set_urls(timeout)

        req = self._request
        coll = req.post(self.tags_url, data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_pipeline_source_files(self, search_params=None, timeout=30):
        """
        Get a paginated list of pipeline source files (data descriptors) given query
        search parameters. If no search parameters is given then get the default first
        page.
        """
        coll = self._fetch_resource('pipeline_source_files_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_pipeline_source_file_by_id(self, id, timeout=30):
        """
        Get a pipeline_source_file's data (descriptors) given its ChRIS id.
        """
        result = self.get_pipeline_source_files({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find pipeline source file with id {id}')

    def upload_pipeline_source_file(self, type, fname, timeout=30):
        """
        Upload a pipeline source file to create a new pipeline. The fname argument
        can be a string indicating a local file path or a file handler.
        """
        if not self.pipeline_source_files_url: self.set_urls(timeout)

        if isinstance(fname, str):
            with open(fname, 'rb') as f:
                file_contents = f.read()
        else:
            file_contents = fname.read()

        data = {'type': type}

        req = self._request
        coll = req.post(self.pipeline_source_files_url, data, file_contents, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_user_files(self, search_params=None, timeout=30):
        """
        Get a paginated list of user files (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('user_files_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_user_file_by_id(self, id, timeout=30):
        """
        Get a user file's data (descriptors) given its ChRIS id.
        """
        result = self.get_user_files({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find user file with id {id}')

    def upload_file(self, upload_path, fname, timeout=30):
        """
        Upload a file to the user's space in CUBE. The fname argument can be a string
        indicating a local file path or a file handler.
        """
        if not self.user_files_url: self.set_urls(timeout)

        if isinstance(fname, str):
            with open(fname, 'rb') as f:
                file_contents = f.read()
        else:
            file_contents = fname.read()

        data = {'upload_path': upload_path}

        req = self._request
        coll = req.post(self.user_files_url, data, file_contents, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def delete_user_file(self, id, timeout=30):
        """
        Delete an existing user file.
        """
        search_params = {'id': id}
        coll = self._fetch_resource('user_files_url', search_params, timeout)
        file_url = coll.items[0].href

        req = self._request
        req.delete(file_url, timeout)

    def get_pacs_files(self, search_params=None, timeout=30):
        """
        Get a paginated list of PACS files (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('pacs_files_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_pacs_file_by_id(self, id, timeout=30):
        """
        Get a PACS file's data (descriptors) given its ChRIS id.
        """
        result = self.get_pacs_files({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find PACS file with id {id}')

    def get_pacs_list(self, search_params=None, timeout=30):
        """
        Get a paginated list of PACS (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('pacs_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_pacs_by_id(self, id, timeout=30):
        """
        Get a PACS's data (descriptors) given its ChRIS id.
        """
        result = self.get_pacs_list({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find PACS with id {id}')

    def get_pacs_queries(self, search_params=None, timeout=30):
        """
        Get a paginated list of PACS queries (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('pacs_queries_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_pacs_query_by_id(self, id, timeout=30):
        """
        Get a PACS query's data (descriptors) given its ChRIS id.
        """
        result = self.get_pacs_queries({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find PACS query with id {id}')

    def create_pacs_query(self, pacs_id, data, timeout=30):
        """
        Create a PACS query given the corresponding PACS id and data dictionary.
        """
        coll = self._fetch_resource('pacs_url', {'id': pacs_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find pacs with id: {pacs_id}.')

        queries_links = Request.get_link_relation_urls(coll.items[0], 'query_list')

        req = self._request
        coll = req.post(queries_links[0], data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def create_pacs_retrieve(self, pacs_query_id, timeout=30):
        """
        Create a PACS retrieve given the corresponding PACS query id.
        """
        coll = self._fetch_resource('pacs_queries_url', {'id': pacs_query_id}, timeout)
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find PACS query with id: '
                                        f'{pacs_query_id}.')

        retrieves_links = Request.get_link_relation_urls(coll.items[0], 'retrieve_list')

        req = self._request
        coll = req.post(retrieves_links[0], {}, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def admin_register_pacs_series(self, data, timeout=30):
        """
        Register a new PACS series with CUBE.
        """
        if not self.pacs_series_url: self.set_urls(timeout)

        req = self._request
        coll = req.post(self.pacs_series_url, data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_pacs_series_list(self, search_params=None, timeout=30):
        """
        Get a paginated list of PACS series (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('pacs_series_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_pacs_series_by_id(self, id, timeout=30):
        """
        Get a PACS series' data (descriptors) given its ChRIS id.
        """
        result = self.get_pacs_series_list({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find PACS series with id {id}')

    def get_file_browser_folders(self, search_params=None, timeout=30):
        """
        Get a paginated list of with the matching file browser folder (the returned
        list only has at most one element) given query search parameters. If no search
        parameters is given then get a list with the default root folder.
        """
        coll = self._fetch_resource('file_browser_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_file_browser_folder_by_id(self, id, timeout=30):
        """
        Get a file browser folder' s data (descriptors) given its ChRIS id.
        """
        result = self.get_file_browser_folders({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find file browser folder with id {id}')

    def get_file_browser_folder_by_path(self, path, timeout=30):
        """
        Get a file browser folder' s data (descriptors) given its ChRIS path.
        """
        result = self.get_file_browser_folders({'path': path}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find file browser folder with path {path}')

    def create_file_browser_folder(self, path, timeout=30):
        """
        Create a file browser folder given the path.
        """
        if not self.file_browser_url: self.set_urls(timeout)

        data = {'path': path}

        req = self._request
        coll = req.post(self.file_browser_url, data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_groups(self, search_params=None, timeout=30):
        """
        Get a paginated list of groups (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        coll = self._fetch_resource('groups_url', search_params, timeout)
        return Request.get_data_from_collection(coll)

    def get_group_by_id(self, id, timeout=30):
        """
        Get a group's data (descriptors) given its ChRIS id.
        """
        result = self.get_groups({'id': id}, timeout)

        if result['data']:
            return result['data'][0]
        raise ChrisRequestException(f'Could not find group with id {id}')

    def admin_create_group(self, data, timeout=30):
        """
        Create a group given the name.
        """
        if not self.groups_url: self.set_urls(timeout)

        req = self._request
        coll = req.post(self.groups_url, data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    def get_user(self, timeout=30):
        """
        Get a user's data (descriptors).
        """
        coll = self._fetch_resource('user_url', None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    @staticmethod
    def create_user(users_url, username, password, email, timeout=30):
        """
        Static method to create a new user account.
        """
        data = {'username': username, 'password': password, 'email': email}

        req = Request()
        coll = req.post(users_url, data, None, timeout)
        result = Request.get_data_from_collection(coll)
        return result['data'][0]

    @staticmethod
    def get_auth_token(auth_url, username, password, timeout=30):
        """
        Static method to fetch a user's login authorization token.
        """
        data = {'username': username, 'password': password}

        req = Request(auth=None, content_type='application/json')
        result = req.post(auth_url, data, None, timeout)
        return result['token']

    def _fetch_resource(self, url_attr, search_params=None, timeout=30):
        """
        Internal method to fetch the collection object of a resource given query search
        parameters. If no search parameters is given then get the default first page.
        """
        url = getattr(self, url_attr)
        if not url: self.set_urls(timeout)

        url = getattr(self, url_attr)
        if not url:
            raise ChrisRequestException('Resource not available to the user.')

        req = self._request

        if search_params:
            collection = req.get(url + self.query_url_sufix, search_params, timeout)
        else:
            collection = req.get(url, None, timeout)
        return collection
