"""
ChRIS API client module.
An item in a collection is represented by a dictionary. A collection of items is
represented by a list of dictionaries.
"""

from .request import Request
from .exceptions import ChrisRequestException


class Client(object):
    """
    A ChRIS API client.
    """

    def __init__(self, url, username, password, timeout=30):
        self.url = url
        self.query_url_sufix = 'search/'
        self.username = username
        self.password = password
        self.timeout = timeout
        self.content_type = 'application/vnd.collection+json'

        # urls of the high level API resources
        self.feeds_url = self.url
        self.files_url = ''
        self.plugins_url = ''
        self.plugin_instances_url = ''
        self.pipelines_url = ''
        self.pipeline_instances_url = ''
        self.tags_url = ''
        self.uploaded_files_url = ''
        self.pacs_files_url = ''
        self.service_files_url = ''
        self.user_url = ''

    def set_urls(self):
        """
        Set the urls of the high level API resources.
        """
        get_url = Request.get_link_relation_urls
        req = Request(self.username, self.password, self.content_type, self.timeout)
        coll = req.get(self.url)

        # get urls of the high level API resources
        self.files_url = self.files_url or get_url(coll, 'files')[0]
        self.plugins_url = self.plugins_url or get_url(coll, 'plugins')[0]
        self.plugin_instances_url = self.plugin_instances_url or get_url(
            coll, 'plugin_instances')[0]
        self.pipelines_url = self.pipelines_url or get_url(coll, 'pipelines')[0]
        self.pipeline_instances_url = self.pipeline_instances_url or get_url(
            coll, 'pipeline_instances')[0]
        self.tags_url = self.tags_url or get_url(coll, 'tags')[0]
        self.uploaded_files_url = self.uploaded_files_url or get_url(
            coll, 'uploadedfiles')[0]
        self.pacs_files_url = self.pacs_files_url or get_url(coll, 'pacsfiles')[0]
        self.service_files_url = self.service_files_url or get_url(
            coll, 'servicefiles')[0]
        self.user_url = self.user_url or get_url(coll, 'user')[0]

    def get_feeds(self, search_params=None):
        """
        Get a paginated list of feed data (descriptors) given query search parameters.
        If no search parameters is given then get the default first page.
        """
        if not self.feeds_url: self.set_urls()
        coll = self._fetch_resource(self.feeds_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_plugins(self, search_params=None):
        """
        Get a paginated list of plugin data (descriptors) given query search parameters.
        If no search parameters is given then get the default first page.
        """
        if not self.plugins_url: self.set_urls()
        coll = self._fetch_resource(self.plugins_url, search_params)
        return Request.get_data_from_collection(coll)

    def get_plugin_by_id(self, id):
        """
        Get a plugin's data (descriptors) given its ChRIS store id.
        """
        search_params = {'id': id}
        result = self.get_plugins(search_params)
        if result['data']:
            return result['data'][0]  # plugin ids are unique
        else:
            raise ChrisRequestException('Could not find plugin with id %s' % id)

    def get_plugin_parameters(self, plugin_id, params=None):
        """
        Get a plugin's paginated parameters given its ChRIS store id.
        """
        if not self.plugins_url: self.set_urls()
        coll = self._fetch_resource(self.plugins_url, {'id': plugin_id})
        if len(coll.items) == 0:
            raise ChrisRequestException('Could not find plugin with id: %s.' % plugin_id)
        parameters_links = Request.get_link_relation_urls(coll.items[0], 'parameters')
        if parameters_links:
            coll = self._fetch_resource(parameters_links[0], params) # there can only be a single parameters link
            return Request.get_data_from_collection(coll)
        return {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}

    def get_pacs_files(self, search_params=None):
        """
        Get a paginated list of PACS files data (descriptors) given query search
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
        req = Request(self.username, self.password, self.content_type, self.timeout)
        coll = req.post(self.pacs_files_url, data)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def get_service_files(self, search_params=None):
        """
        Get a paginated list of service files data (descriptors) given query search
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
        req = Request(self.username, self.password, self.content_type, self.timeout)
        coll = req.post(self.service_files_url, data)
        result = req.get_data_from_collection(coll)
        return result['data'][0]

    def _fetch_resource(self, url, search_params=None):
        """
        Fetch the collection object of a resource given query search parameters.
        If no search parameters is given then get the default first page.
        """
        req = Request(self.username, self.password, self.content_type, self.timeout)
        if search_params:
            collection = req.get(url + self.query_url_sufix, search_params)
        else:
            collection = req.get(url)
        return collection
