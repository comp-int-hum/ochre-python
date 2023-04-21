import logging
from requests import Session
import yaml


logger = logging.getLogger(__name__)


class Connection(Session):

    def __init__(self, config):
        super(Connection, self).__init__()
        self.user = config.get("user")
        self.session = Session()
        if self.user:
            self.session.auth = (self.user, config.get("password"))

        self.session.headers = {"Accept" : "application/vnd.oai.openapi"}            
        x = self.session.get(
            "{protocol}://{hostname}:{port}/openapi/".format(**config),
        )
        self.openapi = yaml.load(x.text, Loader=yaml.FullLoader)
            
        self.session.headers = {"Accept" : "application/json"}
        self.hostname = "{protocol}://{hostname}/".format(**config)
        self.base_url = "{protocol}://{hostname}:{port}{path}/".format(**config)


        try:
            resp = self.session.get(self.base_url)
        except Exception as e:
            logger.info(
                "Could not connect to OCHRE server: %s",
                e
            )
            return
        if resp.status_code == 403:
            logger.warn("Connected to, but could not authenticate with, server with user '%s' and the provided password.  Falling back to AnonymousUser.", self.user)
            self.session.auth = None
            resp = self.session.get(self.base_url)
        if resp.status_code != 200:
            logger.warn("Could not connect to server via '%s://%s:%s%s/'", config.get("protocol"), config.get("hostname"), config.get("port"), config.get("path"))
            raise Exception(resp.reason)
        self.endpoints = resp.json()

    def action(self, action_name, url, data=None, expected=None, files={}):
        files = {k : open(v, "rb") if isinstance(v, str) else v for k, v in files.items()}
        resp = getattr(self.session, action_name)(url, data=data, files=files)
        if expected and resp.status_code != expected:
            raise Exception("Expected {} but got {} ({})".format(expected, resp.status_code, resp.reason))
        try:
            return resp.json() if resp.ok == True else {}
        except:
            return {}

    def get_objects(self, model_name):
        return self.get(self.endpoints[model_name])
        
    def get(self, url, data=None, expected=None, follow_next=True):
        if follow_next:
            resp = self.action("get", url, data=data, expected=expected)
            retval = {k : v for k, v in resp.items()}
            while resp["next"]:
                resp = self.action("get", resp["next"], data=data, expected=expected)
                for res in resp["results"]:
                    retval["results"].append(res)
            retval["count"] = len(retval["results"])
            retval["next"] = None
            return retval
        else:
            return self.action("get", url, data=data, expected=expected)

    def post(self, url, data, expected=None, files={}):
        return self.action("post", url=url, data=data, expected=expected, files=files)

    def put(self, url, data, expected=None, files={}):
        return self.action("put", url, data=data, expected=expected, files=files)
        
    def patch(self, url, data, expected=None, files={}):
        return self.action("patch", url, data, expected=expected, files=files)

    def delete(self, url, data=None, expected=None):
        return self.action("delete", url, data, expected)

    def create(self, model_name, data, expected=None, files={}):
        return self.post(self.endpoints[model_name], data, files=files)

    def replace(self, url, data, expected=None):
        return self.put(url, data, expected)

    def update(self, url, data, expected=None, files={}):
        self.patch(url, data, expected, files)

    def get_object(self, model_name, object_name):
        retval = None
        for obj in self.get(self.endpoints[model_name])["results"]:
            if obj.get("name", None) == object_name:
                if retval != None:
                    raise Exception("There are more than one '{}' objects with name '{}' (this should never happen!)".format(model_name, object_name))
                else:
                    retval = obj
        return retval

    def create_object(self, model_name, data, files={}, expected=None):
        return self.create(model_name, data=data, files=files, expected=expected)
    
    def create_or_replace_object(self, model_name, object_name, data, files={}):
        cur = self.get_object(model_name, object_name)
        if cur:
            return self.put(cur["url"], data=data, files=files)
        else:
            data["name"] = object_name            
            return self.create_object(model_name, data=data, files=files)
        
    def create_or_update_object(self, model_name, object_name, data, files={}):
        cur = self.get_object(model_name, object_name)
        if cur:            
            return self.patch(cur["url"], data=data, files=files)
        else:
            data["name"] = object_name
            return self.create_object(model_name, data=data, files=files)

    def delete_object(self, model_name, object_name):
        cur = self.get_object(model_name, object_name)
        if cur:            
            return self.delete(cur["url"])
        else:
            pass

    def invoke(self, path, data, files={}):
        return self.post(
            "{}{}".format(self.base_url, path),
            data=data,
            files=files,
            expected=None
        )
