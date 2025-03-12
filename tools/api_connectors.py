import requests
from github import Github
from googleapiclient.discovery import build

class APIConnectors:
    def __init__(self):
        pass

    def generic_rest_client(self, url, method='GET', headers=None, params=None, data=None):
        response = requests.request(method, url, headers=headers, params=params, data=data)
        return response.json()

    def github_connector(self, token):
        return Github(token)

    def google_connector(self, api_name, api_version, developer_key):
        return build(api_name, api_version, developerKey=developer_key)
def infer_schema(self, url, method='GET', headers=None, params=None, data=None):
        response = requests.request(method, url, headers=headers, params=params, data=data)
        schema = {
            'url': url,
            'method': method,
            'headers': headers,
            'params': params,
            'data': data,
            'response': response.json()
        }
        return schema
