import logging
from requests import Session


logger = logging.getLogger(__name__)


class Connection(Session):

    def __init__(self, config):
        super(Connection, self).__init__()
        self.user = config.get("user")
        self.session = Session()
        self.session.auth = (self.user, config.get("password"))
        self.session.headers = {"Accept" : "application/json"}
        self.base_url = "{protocol}://{hostname}:{port}{path}/".format(**config)
        resp = self.session.get(self.base_url)        
        if resp.status_code != 200:
            raise Exception(resp.reason)
        self.endpoints = resp.json()
            
    def action(self, action_name, url, data=None, expected=None, files=None):
        resp = getattr(self.session, action_name)(url, data=data, files=files)
        if expected and resp.status_code != expected:
            raise Exception("Expected {} but got {}".format(expected, resp.status_code))
        try:
            return resp.json() if resp.ok == True else {}
        except:
            return {}

    def get_objects(self, model_name):
        return self.get(self.endpoints[model_name])
        
    def get(self, url, data=None, expected=200, follow_next=True):
        if follow_next:
            resp = self.action("get", url, data, expected)
            retval = {k : v for k, v in resp.items()}
            while resp["next"]:
                resp = self.action("get", resp["next"], data, expected)
                for res in resp["results"]:
                    retval["results"].append(res)
            retval["count"] = len(retval["results"])
            retval["next"] = None
            return retval
        else:
            return self.action("get", url, data, expected)

    def post(self, url, data, expected=201, files=None):
        return self.action("post", url=url, data=data, expected=expected, files=files)

    # def put(self, url, data, expected=200):
    #     return self.action("put", url, data, expected)
        
    def patch(self, url, data, expected=200):
        return self.action("patch", url, data, expected)

    def delete(self, url, data=None, expected=200):
        return self.action("delete", url, data, expected)

    def create(self, model_name, data):
        return self.post(self.endpoints[model_name], data)
