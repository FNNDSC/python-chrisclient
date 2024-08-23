
import json
from random import randint
from unittest import TestCase
from unittest import mock

from chrisclient import client


class ClientTests(TestCase):

    def setUp(self):
        self.chris_url = "http://localhost:8000/api/v1/"
        self.username = "cube"
        self.password = "cube1234"
        self.client = client.Client(self.chris_url, self.username, self.password)

    def test_get_feed_by_id(self):
        """
        Test whether get_feed_by_id method can get a feed representation from CUBE.
        """
        response = self.client.get_feed_by_id(1)
        self.assertEqual(response['id'], 1)

    def test_get_plugin_by_id(self):
        """
        Test whether get_plugin_by_id method can get a plugin representation from CUBE.
        """
        response = self.client.get_plugin_by_id(1)
        self.assertEqual(response['id'], 1)

    def test_get_plugin_by_id_unauthenticated(self):
        """
        Test whether get_plugin_by_id method can get a plugin representation from CUBE
        for unauthenticated users.
        """
        cl = client.Client(self.chris_url)
        response = cl.get_plugin_by_id(1)
        self.assertEqual(response['id'], 1)

    def test_get_plugin_parameters(self):
        """
        Test whether get_plugin_parameters method can get the list of all plugin parameter
        representations for the given plugin from CUBE.
        """
        plugin_id = 2
        response = self.client.get_plugin_parameters(plugin_id,
                                                     {'limit': 50, 'offset': 0})
        self.assertEqual(response['data'][0]['name'], "dir")

    def test_get_plugin_parameters_unauthenticated(self):
        """
        Test whether get_plugin_parameters method can get the list of all plugin parameter
        representations for the given plugin from CUBE for unauthenticated users.
        """
        cl = client.Client(self.chris_url)
        plugin_id = 2
        response = cl.get_plugin_parameters(plugin_id, {'limit': 50, 'offset': 0})
        self.assertEqual(response['data'][0]['name'], "dir")

    def test_get_plugins_with_no_args(self):
        """
        Test whether get_plugins method can get the list of all plugin representations
        from CUBE.
        """
        response = self.client.get_plugins()
        self.assertGreater(len(response['data']), 1)

    def test_get_plugins_with_no_args_unauthenticated(self):
        """
        Test whether get_plugins method can get the list of all plugin representations
        from CUBE for unauthenticated users.
        """
        cl = client.Client(self.chris_url)
        response = cl.get_plugins()
        self.assertGreater(len(response['data']), 1)

    def test_get_plugins_with_search_args(self):
        """
        Test whether get_plugins method can get a list of plugin representations
        from CUBE given query search parameters.
        """
        response = self.client.get_plugins({'name_exact': "pl-dircopy"})
        self.assertEqual(response['data'][0]['name'], "pl-dircopy")

    def test_create_plugin_instance(self):
        """
        Test whether create_plugin_instance method can create a new plugin instance
        through the REST API.
        """
        plugin_id = 2
        data = {
            'title': 'Test plugin instance',
            'dir': 'home/' + self.username + '/uploads'
        }
        response = self.client.create_plugin_instance(plugin_id, data)
        self.assertEqual(response['title'], data['title'])

    def test_get_pipeline_by_id(self):
        """
        Test whether get_pipeline_by_id method can get a pipeline representation from
        CUBE.
        """
        response = self.client.get_pipeline_by_id(2)
        self.assertEqual(response['id'], 2)

    def test_get_pipeline_default_parameters(self):
        """
        Test whether get_pipeline_default_parameters method can get the list of all
        pipeline parameter representations for the given pipeline from CUBE.
        """
        pipeline_id = 2
        response = self.client.get_pipeline_default_parameters(pipeline_id,
                                                               {'limit': 50, 'offset': 0})
        self.assertEqual(response['total'], 18)

    def test_get_pipeline_default_parameters_unauthenticated(self):
        """
        Test whether get_pipeline_default_parameters method can get the list of all
        pipeline parameter representations for the given pipeline from CUBE for
        unauthenticated users.
        """
        cl = client.Client(self.chris_url)
        pipeline_id = 2
        response = cl.get_pipeline_default_parameters(pipeline_id,
                                                      {'limit': 50, 'offset': 0})
        self.assertEqual(response['total'], 18)

    def test_create_workflow(self):
        """
        Test whether create_workflow method can create a new workflow through the REST
        API.
        """
        pipeline_id = 2
        nodes = [
            {"piping_id": 3, "compute_resource_name": "host",
             "plugin_parameter_defaults": [{"name": "prefix", "default": "test"},
                                           {"name": "dummyInt", "default": 3}]},
            {"piping_id": 4, "compute_resource_name": "host"},
            {"piping_id": 5, "compute_resource_name": "host"}
        ]
        data = {
            'title': 'Workflow1',
            'previous_plugin_inst_id': 1,
            'nodes_info': json.dumps(nodes)
        }
        response = self.client.create_workflow(pipeline_id, data)
        workflow_title = response['title']
        self.assertEqual(workflow_title, data['title'])
        workflow_id = response['id']
        response = self.client.get_workflow_plugin_instances(workflow_id, data)
        self.assertEqual(response['total'], 3)

    def test_get_user(self):
        """
        Test whether get_user method can get a user representation from CUBE.
        """
        response = self.client.get_user()
        self.assertEqual(response['username'], 'cube')

    def test_create_user(self):
        """
        Test whether static create_user method can create a new user account
        through the REST API.
        """
        username = f'cube{randint(1000,9000)}'
        password = f'{username}1234'
        email = f'{username}@gmail.com'
        response = client.Client.create_user('http://localhost:8000/api/v1/users/',
                                             username, password, email)
        self.assertEqual(response['username'], username)
