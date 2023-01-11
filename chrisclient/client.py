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

    def __init__(self, url, username=None, password=None, timeout=30):
        self.url = url
        self.query_url_sufix = 'search/'
        self.username = username
        self.password = password
        self.timeout = timeout
        self.content_type = 'application/vnd.collection+json'

        # urls of the high level API resources
        self.feeds_url = self.url
        self.chris_instance_url = ''
        self.admin_url = ''
        self.files_url = ''
        self.compute_resources_url = ''
        self.plugin_metas_url = ''
        self.plugins_url = ''
        self.plugin_instances_url = ''
        self.pipelines_url = ''
        self.pipeline_instances_url = ''
        self.workflows_url = ''
        self.tags_url = ''
        self.uploaded_files_url = ''
        self.pacs_files_url = ''
        self.service_files_url = ''
        self.file_browser_url = ''
        self.user_url = ''

    def set_urls(self):
        """
        Set the urls of the high level API resources.
        """
        get_url = Request.get_link_relation_urls
        req = Request(self.username, self.password, self.content_type)
        coll = req.get(self.url, None, self.timeout)

        # get urls of the high level API resources
        self.chris_instance_url = self.chris_instance_url or get_url(
            coll, 'chrisinstance')[0]
        self.files_url = self.files_url or get_url(coll, 'files')[0]
        self.compute_resources_url = self.compute_resources_url or get_url(
            coll, 'compute_resources')[0]
        self.plugin_metas_url = self.plugin_metas_url or get_url(coll, 'plugin_metas')[0]
        self.plugins_url = self.plugins_url or get_url(coll, 'plugins')[0]
        self.plugin_instances_url = self.plugin_instances_url or get_url(
            coll, 'plugin_instances')[0]
        self.pipelines_url = self.pipelines_url or get_url(coll, 'pipelines')[0]
        self.pipeline_instances_url = self.pipeline_instances_url or get_url(
            coll, 'pipeline_instances')[0]
        self.workflows_url = self.workflows_url or get_url(coll, 'workflows')[0]
        self.tags_url = self.tags_url or get_url(coll, 'tags')[0]
        self.uploaded_files_url = self.uploaded_files_url or get_url(
            coll, 'uploadedfiles')[0]
        self.pacs_files_url = self.pacs_files_url or get_url(coll, 'pacsfiles')[0]
        self.service_files_url = self.service_files_url or get_url(
            coll, 'servicefiles')[0]
        self.file_browser_url = self.file_browser_url or get_url(coll, 'filebrowser')[0]
        if self.username:
            self.user_url = self.user_url or get_url(coll, 'user')[0]
            if not self.admin_url:
                urls = get_url(coll, 'admin')
                if urls:
                    self.admin_url = urls[0]

    def get_feeds(self, search_params=None):
        """
        Get a paginated list of feeds (data descriptors) given query search parameters.
        If no search parameters is given then get the default first page.
        """
        if not self.feeds_url: self.set_urls()
        coll = self._fetch_resource(self.feeds_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_plugins(self, search_params=None):
        """
        Get a paginated list of plugins (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.plugins_url: self.set_urls()
        coll = self._fetch_resource(self.plugins_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_plugin_by_id(self, id):
        """
        Get a plugin's data (descriptors) given its ChRIS id.
        """
        search_params = {'id': id}
        result = self.get_plugins(search_params)
        if result['data']:
            return result['data'][0]  # plugin ids are unique
        else:
            raise ChrisRequestException(f'Could not find plugin with id {id}')

    def get_plugin_parameters(self, plugin_id, params=None):
        """
        Get a plugin's paginated parameters given its ChRIS id.
        """
        if not self.plugins_url: self.set_urls()
        coll = self._fetch_resource(self.plugins_url, {'id': plugin_id})
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find plugin with id: {plugin_id}.')
        parameters_links = Request.get_link_relation_urls(coll.items[0], 'parameters')
        if parameters_links:
            req = Request(self.username, self.password, self.content_type)
            coll = req.get(parameters_links[0], params, self.timeout) # there can only be a single parameters link
            return Request.get_data_from_collection(coll)
        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def admin_upload_plugin(self, compute_names, data):
        """
        Upload a plugin representation file and create a new plugin. The data argument
        can be:
            * a string indicating a local file path, or
            * a file handler, or
            * a python dictionary representation.
        """
        if not self.admin_url: self.set_urls()
        if not self.admin_url:
            raise ChrisRequestException(f"User '{self.username}' is not a ChRIS admin.")
        if isinstance(data, str):
            with open(data, 'rb') as f:
                file_contents = f.read()
        elif type(data) is dict:
            file_contents = json.dumps(data, indent = 4).encode('utf-8')
        else:
            file_contents = fname.read()
        req = Request(self.username, self.password, self.content_type)
        comp = {'compute_names': compute_names}
        coll = req.post(self.admin_url, comp, file_contents, self.timeout)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def get_plugin_instances(self, search_params=None):
        """
        Get a paginated list of plugin instances (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.plugin_instances_url: self.set_urls()
        coll = self._fetch_resource(self.plugin_instances_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_plugin_instance_by_id(self, id):
        """
        Get a plugin instance's data (descriptors) given its ChRIS id.
        """
        search_params = {'id': id}
        result = self.get_plugin_instances(search_params)
        if result['data']:
            return result['data'][0]
        else:
            raise ChrisRequestException(f'Could not find plugin instance with id {id}')

    def create_plugin_instance(self, plugin_id, data):
        """
        Create a plugin instance given the corresponding plugin id and plugin-specific
        data dictionary.
        """
        if not self.plugins_url: self.set_urls()
        coll = self._fetch_resource(self.plugins_url, {'id': plugin_id})
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find plugin with id: {plugin_id}.')
        instances_links = Request.get_link_relation_urls(coll.items[0], 'instances')
        req = Request(self.username, self.password, self.content_type)
        coll = req.post(instances_links[0], data, None, self.timeout)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def get_pipelines(self, search_params=None):
        """
        Get a paginated list of pipelines (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.pipelines_url: self.set_urls()
        coll = self._fetch_resource(self.pipelines_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_pipeline_by_id(self, id):
        """
        Get a pipeline's data (descriptors) given its ChRIS id.
        """
        search_params = {'id': id}
        result = self.get_pipelines(search_params)
        if result['data']:
            return result['data'][0]  # pipeline ids are unique
        else:
            raise ChrisRequestException(f'Could not find pipeline with id {id}')

    def get_pipeline_default_parameters(self, pipeline_id, params=None):
        """
        Get a pipeline's paginated default parameters given its ChRIS id.
        """
        if not self.pipelines_url: self.set_urls()
        coll = self._fetch_resource(self.pipelines_url, {'id': pipeline_id})
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find pipeline with id: '
                                        f'{pipeline_id}.')
        parameters_links = Request.get_link_relation_urls(coll.items[0],
                                                          'default_parameters')
        if parameters_links:
            req = Request(self.username, self.password, self.content_type)
            coll = req.get(parameters_links[0], params, self.timeout)
            return Request.get_data_from_collection(coll)
        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def create_pipeline(self, data):
        """
        Create a pipeline given the data dictionary.
        """
        if not self.pipelines_url: self.set_urls()
        req = Request(self.username, self.password, self.content_type)
        coll = req.post(self.pipelines_url, data, None, self.timeout)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def get_workflows(self, search_params=None):
        """
        Get a paginated list of workflows (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.workflows_url: self.set_urls()
        coll = self._fetch_resource(self.workflows_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_workflow_by_id(self, id):
        """
        Get a workflow's data (descriptors) given its ChRIS id.
        """
        search_params = {'id': id}
        result = self.get_workflows(search_params)
        if result['data']:
            return result['data'][0]
        else:
            raise ChrisRequestException(f'Could not find workflow with id {id}')

    def get_workflow_plugin_instances(self, workflow_id, params=None):
        """
        Get a workflow's paginated list of plugin instances given its ChRIS id.
        """
        if not self.workflows_url: self.set_urls()
        coll = self._fetch_resource(self.workflows_url, {'id': workflow_id})
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find workflow with id: {workflow_id}.')
        parameters_links = Request.get_link_relation_urls(coll.items[0],
                                                          'plugin_instances')
        if parameters_links:
            req = Request(self.username, self.password, self.content_type)
            coll = req.get(parameters_links[0], params, self.timeout)
            return Request.get_data_from_collection(coll)
        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def create_workflow(self, pipeline_id, data):
        """
        Create a workflow given the corresponding pipeline id and pipeline-specific
        data dictionary.
        """
        if not self.pipelines_url: self.set_urls()
        coll = self._fetch_resource(self.pipelines_url, {'id': pipeline_id})
        if len(coll.items) == 0:
            raise ChrisRequestException(f'Could not find pipeline with id: '
                                        f'{pipeline_id}.')
        workflows_links = Request.get_link_relation_urls(coll.items[0], 'workflows')
        req = Request(self.username, self.password, self.content_type)
        coll = req.post(workflows_links[0], data, None, self.timeout)
        result = req.get_data_from_collection(coll)
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

    def get_pacs_files(self, search_params=None):
        """
        Get a paginated list of PACS files (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.pacs_files_url: self.set_urls()
        coll = self._fetch_resource(self.pacs_files_url, search_params)
        return Request.get_data_from_collection(coll)

    def register_pacs_file(self, data):
        """
        Register a new PACS file with CUBE.
        """
        if not self.pacs_files_url: self.set_urls()
        req = Request(self.username, self.password, self.content_type)
        coll = req.post(self.pacs_files_url, data, None, self.timeout)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def get_service_files(self, search_params=None):
        """
        Get a paginated list of service files (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.service_files_url: self.set_urls()
        coll = self._fetch_resource(self.service_files_url, search_params)
        return Request.get_data_from_collection(coll)

    def register_service_file(self, data):
        """
        Register a new PACS file with CUBE.
        """
        if not self.service_files_url: self.set_urls()
        req = Request(self.username, self.password, self.content_type)
        coll = req.post(self.service_files_url, data, None, self.timeout)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def upload_file(self, upload_path, fname):
        """
        Upload a file to the user's uploads in CUBE. The fname argument can be a string
        indicating a local file path or a file handler.
        """
        if not self.uploaded_files_url: self.set_urls()
        if isinstance(fname, str):
            with open(fname, 'rb') as f:
                file_contents = f.read()
        else:
            file_contents = fname.read()
        req = Request(self.username, self.password, self.content_type)
        data = {'upload_path': upload_path}
        coll = req.post(self.uploaded_files_url, data, file_contents, self.timeout)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def get_uploaded_files(self, search_params=None):
        """
        Get a paginated list of uploaded files (data descriptors) given query search
        parameters. If no search parameters is given then get the default first page.
        """
        if not self.uploaded_files_url: self.set_urls()
        coll = self._fetch_resource(self.uploaded_files_url, search_params)
        return Request.get_data_from_collection(coll)

    def delete_uploaded_file(self, id):
        """
        Delete an existing uploaded file.
        """
        if not self.uploaded_files_url: self.set_urls()
        search_params = {'id': id}
        coll = self._fetch_resource(self.uploaded_files_url, search_params)
        file_url = coll.items[0].href
        req = Request(self.username, self.password, self.content_type)
        req.delete(file_url, self.timeout)

    def _fetch_resource(self, url, search_params=None):
        """
        Fetch the collection object of a resource given query search parameters.
        If no search parameters is given then get the default first page.
        """
        req = Request(self.username, self.password, self.content_type)
        if search_params:
            collection = req.get(url + self.query_url_sufix, search_params, self.timeout)
        else:
            collection = req.get(url, None, self.timeout)
        return collection
