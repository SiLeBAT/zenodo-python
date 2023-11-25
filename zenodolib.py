"""
Copyright (c) 2015 Federal Institute for Risk Assessment (BfR), Germany

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
    Department Biological Safety - BfR
"""
import enum
import json

import requests


class StatusCode(enum.Enum):
    ok = 200
    created = 201
    accepted = 202
    no_content = 204
    bad_request = 400
    unathorized = 401
    forbidden = 403
    not_found = 404
    method_not_allowed = 405
    conflict = 409
    payload_too_large = 413
    unsupported_media_type = 415
    too_many_requests = 429
    internal_server_error = 500


class ZenodoHandler:
    def __init__(self, access_token, proxies=None, test=False):
        """
        Initializes ZenodoHandler.

        :param access_token: Personal access token
        :param proxies: Dictionary with proxies for each protocol. E.g::

          {'http:': 'my_http_proxy.com:port', 'ftp': 'my_ftp_proxy.com:port'}

        :param test: Boolean. If True connects to Zenodo sandbox environment,
          otherwise connects to Zenodo.
        """

        if test:
            self.base_url = "https://sandbox.zenodo.org/api/"
        else:
            self.base_url = "https://zenodo.org/api/"

        self.token = access_token
        self.session = requests.Session()
        self.session.proxies.update(proxies)
        self.session.params['access_token'] = access_token

    def deposition_list(self):
        """
        List all depositions for the currently authenticated user.

        - Path: /api/deposit/depositions
        - Method: GET
        """
        url = "{}deposit/depositions".format(self.base_url)
        return self.session.get(url)

    def deposition_create(self):
        """
        Create a new deposition resource.

        - Path: /api/deposit/depositions
        - Method: POST

        : param deposition_id: Deposition identifier
        """
        url = "{}deposit/depositions".format(self.base_url)
        headers = {"Content-Type": "application/json"}
        return self.session.post(url, data="{}", headers=headers)

    def deposition_retrieve(self, deposition_id):
        """
        Retrieve a single deposition resource.

        - Path: /api/deposit/depositions/:id
        - Method: GET

        :param deposition_id: Deposition identifier
        """
        url = "{}deposit/depositions/{}".format(self.base_url, deposition_id)
        return self.session.get(url)

    def deposition_update(self, deposition_id, data):
        """
        Update an existing deposition resource.

        - Path: /api/deposit/depositions/:id
        - Method: PUT

        :param deposition_id: Deposition identifier
        :param data: Data to upload
        """
        url = "{}deposit/depositions/{}".format(self.base_url, deposition_id)
        headers = {"Content-Type": "application/json"}
        return self.session.put(url, data=json.dumps(data), headers=headers)

    def deposition_delete(self, deposition_id):
        """
        Delete an existing deposition resource.

        - Path: /api/deposit/depositions/:id
        - Method: DELETE

        :param deposition_id: Deposition identifier
        """
        url = "{}deposit/depositions/{}".format(self.base_url, deposition_id)
        return self.session.delete(url)

    def deposition_files_list(self, deposition_id):
        """
        List all deposition files for a given deposition.

        - Path: /api/deposit/depositions/:id/files
        - Method: GET

        :param deposition_id: Deposition identifier
        """
        url = "{}deposit/depositions/{}/files".format(
            self.base_url, deposition_id)
        return self.session.get(url)

    def deposition_files_create(self, deposition_id, target_name, file_path):
        """
        Upload a new file.

        - Path: /api/files/:bucket_url/:target_name
        - Methods: PUT

        :param deposition_id: Deposition identifier
        :param target_name: Name of the file once uploaded
        :param file_path: Path to local file to be uploaded
        """
        r = self.deposition_retrieve(deposition_id)
        bucket_url = r.json()['links']['bucket']
        url = "{}/{}".format(bucket_url, target_name)
        # data = {'file': open(file_path, 'rb')}
        # adaptation to new API, as commented in https://github.com/SiLeBAT/zenodo-python/issues/6 
        # context manager approach:
        with open(file_path, 'rb') as fp:
            headers = {"Accept": "application/json",
                       "Content-Type": "application/octet-stream"}
            return self.session.put(url, data=fp, headers=headers)

    def deposition_files_sort(self, deposition_id, file_ids):
        """
        Sort the files for a deposition. By default, the first file is show

        - Path: /api/deposit/depositions/:id/files
        - Method: PUT

        :param deposition_id: Deposition identifier
        :param file_ids: List of ids of the files in the deposition
        """
        url = "{}deposit/depositions/{}/files".format(
            self.base_url, deposition_id)
        headers = {"Content-Type": "application/json"}
        data = json.dumps({'id': file_id for file_id in file_ids})
        return self.session.put(url, data=data, headers=headers)

    def deposition_files_retrieve(self, deposition_id, file_id):
        """
        Retrieve a single deposition file.

        - Path: /api/deposit/depositions/:id/files/:file_id
        - Method: GET

        :param deposition_id: Deposition identifier
        :param file_id: Deposition file identifier
        """
        url = "{}deposit/depositions/{}/files/{}".format(
            self.base_url, deposition_id, file_id)
        return self.session.get(url)

    def deposition_files_update(self, deposition_id, file_id, target_name):
        """
        Update a deposition file resource.
        Currently the only use is renaming an already uploaded file.
        If you want to to replace the actual file, please
        delete the file and upload new file.

        - Path: /api/deposit/depositions/:id/files/:file_id
        - Method: PUT

        :param deposition_id: Deposition identifier
        :param file_id: Deposition file identifier
        :param target_name: Name of the file once uploaded
        """
        url = "{}deposit/depositions/{}/files/{}".format(
            self.base_url, deposition_id, file_id)
        headers = {"Content-Type": "application/json"}
        data = json.dumps({"filename", target_name})

        return self.session.put(url, data=data, headers=headers)

    def deposition_files_delete(self, deposition_id, file_id):
        """
        Delete an existing deposition file resource.
        Note, only deposition files for unpublished depositions may be deleted.

        - Path: /api/deposit/depositions/:id/files/:file_id
        - Method: DELETE

        :param deposition_id: Deposition identifier
        :param file_id: Deposition file id
        """
        url = "{}deposit/depositions/{}/files/{}".format(
            self.base_url, deposition_id, file_id)
        return self.session.delete(url)

    def deposition_actions_publish(self, deposition_id):
        """
        Publish a deposition. Note, once a deposition is published, you can
        no longer delete it.

        - Path: /api/deposit/depositions/:id/actions/publish
        - Method: POST

        :param deposition_id: Deposition identifier.
        """
        url = "{}deposit/depositions/{}/actions/publish".format(
            self.base_url, deposition_id)
        return self.session.post(url)

    def deposition_actions_edit(self, deposition_id):
        """
        Unlock already submitted deposition for editing.

        - Path: /api/deposit/depositions/:id/actions/edit
        - Method: POST

        :param deposition_id: Deposition identifier.
        """
        url = "{}deposit/depositions/{}/actions/edit".format(
            self.base_url, deposition_id)
        return self.session.post(url)

    def deposition_actions_discard(self, deposition_id):
        """
        Discard changes in the current editing session.

        - Path: /api/deposit/depositions/:id/actions/discard
        - Method: POST

        :param deposition_id: Deposition identifier
        """
        url = "{}deposit/depositions/{}/actions/discard".format(
            self.base_url, deposition_id)
        return self.session.post(url)

    def deposition_actions_newversion(self, deposition_id):
        """
        Creates a new version of an existing deposition resource.

        - Path: /api/deposit/depositions/:id/actions/newversion
        - Method: POST

        :param deposition_id: Deposition identifier
        """
        url = "{}deposit/depositions/{}/actions/newversion".format(
            self.base_url, deposition_id)
        return self.session.post(url)
