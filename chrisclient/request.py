"""
ChRIS request module.
"""

import json
import requests
from collection_json import Collection

from.exceptions import ChrisRequestException


class Request(object):
    """
    Http request object.
    """

    def __init__(self, username, password, content_type, timeout=30):
        self.username = username
        self.password = password
        self.content_type = content_type
        self.timeout = timeout

    def get(self, url, params=None):
        """
        Make a GET request to CUBE.
        """
        headers = {'Content-Type': self.content_type, 'Accept': self.content_type}
        try:
            if self.username or self.password:
                r = requests.get(url,
                                 params=params,
                                 auth=(self.username, self.password),
                                 timeout=self.timeout, headers=headers)
            else:
                r = requests.get(url, params=params, timeout=self.timeout,
                                 headers=headers)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ChrisRequestException(str(e))
        return self.get_collection_from_response(r)

    def post(self, url, data, descriptor_file=None):
        """
        Make a POST request to CUBE.
        """
        return self._post_put(requests.post, url, data, descriptor_file)

    def put(self, url, data, descriptor_file=None):
        """
        Make a PUT request to CUBE.
        """
        return self._post_put(requests.put, url, data, descriptor_file)

    def delete(self, url):
        """
        Make a DELETE request to CUBE.
        """
        try:
            if self.username or self.password:
                r = requests.delete(url,
                                    auth=(self.username, self.password),
                                    timeout=self.timeout)
            else:
                r = requests.delete(url, timeout=self.timeout)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ChrisRequestException(str(e))

    def _post_put(self, request_method, url, data, descriptor_file=None):
        """
        Internal method to make either a POST or PUT request to CUBE.
        """
        if descriptor_file is None:
            headers = {'Content-Type': self.content_type, 'Accept': self.content_type}
            files = None
            data = json.dumps(self.makeTemplate(data))
        else:
            # this is a multipart request
            headers = None
            files = {'descriptor_file': descriptor_file}
        try:
            if self.username or self.password:
                r = request_method(url, files=files, data=data,
                                   auth=(self.username, self.password),
                                   timeout=self.timeout, headers=headers)
            else:
                r = request_method(url, files=files, data=data, timeout=self.timeout,
                                   headers=headers)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            raise ChrisRequestException(str(e))
        return self.get_collection_from_response(r)

    @staticmethod
    def get_data_from_collection(collection):
        """
        Get the result data dictionary from a collection object.
        """
        result = {'data': [], 'hasNextPage': False, 'hasPreviousPage': False, 'total': 0}
        for item in collection.items:
            item_dict = Request.get_item_descriptors(item)
            result['data'].append(item_dict)
        if Request.get_link_relation_urls(collection, 'next'):
            result['hasNextPage'] = True
        if Request.get_link_relation_urls(collection, 'previous'):
            result['hasPreviousPage'] = True
        if hasattr(collection, 'total'):
            result['total'] = collection.total
        return result

    @staticmethod
    def get_item_descriptors(item):
        """
        Get an item's data (descriptors) in a dictionary.
        """
        item_dict = {}
        # collect the item's descriptors
        for descriptor in item.data:
            item_dict[descriptor.name] = descriptor.value
        return item_dict

    @staticmethod
    def get_link_relation_urls(obj, relation_name):
        """
        Static method to get the list of urls for a link relation in a collection or
        item object.
        """
        return [link.href for link in obj.links if link.rel == relation_name]

    @staticmethod
    def get_collection_from_response(response):
        """
        Static method to get the collection object from a response object.
        """
        content = json.loads(response.text)
        total = content['collection'].pop('total', None)
        collection = Collection.from_json(json.dumps(content))
        if collection.error:
            raise ChrisRequestException(collection.error.message)
        if total is not None:
            collection.total = total
        return collection

    @staticmethod
    def makeTemplate(descriptors_dict):
        """
        Static method to make a Collection+Json template from a regular dictionary whose
        properties are the item descriptors.
        """
        template = {'data': []}
        for key in descriptors_dict:
            template['data'].append({'name': key, 'value': descriptors_dict[key]})
        return {'template': template}
