

import io
import json
from unittest import TestCase
from unittest import mock

from chrisclient import client


class ClientTests(TestCase):

    def setUp(self):
        self.chris_url = "http://localhost:8000/api/v1/"
        self.username = "cube"
        self.password = "cube1234"
        self.client = client.Client(self.chris_url, self.username, self.password)

    def test_get_plugin_by_id(self):
        """
        Test whether get_plugin_by_id method can get a plugin representation from CUBE.
        """
        response = self.client.get_plugin_by_id(1)
        self.assertEqual(response['id'], 1)

    def test_get_plugin_parameters(self):
        """
        Test whether get_plugin_parameters method can get the list of all plugin parameter
        representations for the given plugin from CUBE.
        """
        plugin_id = 1
        response = self.client.get_plugin_parameters(plugin_id)
        print('response:', response)
        self.assertEqual(response['data'][0]['name'], "dir")

    def test_get_plugins_with_no_args(self):
        """
        Test whether get_plugins method can get the list of all plugin representations
        from CUBE.
        """
        response = self.client.get_plugins()
        self.assertGreater(len(response['data']), 1)

    def test_get_plugins_with_search_args(self):
        """
        Test whether get_plugins method can get a list of plugin representations
        from CUBE given query search parameters.
        """
        response = self.client.get_plugins({'name_exact': "simplefsapp"})
        self.assertEqual(response['data'][0]['name'], "simplefsapp")
