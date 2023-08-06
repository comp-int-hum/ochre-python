import logging
from requests import Session
import yaml
from pyochre import env


logger = logging.getLogger(__name__)


class Connection(Session):

    def __init__(self, config=None):
        super(Connection, self).__init__()
        self.user = env("USER")
        self.session = Session()
        if self.user:
            self.session.auth = (self.user, env("PASSWORD"))
        self.session.headers = {"Accept" : "application/vnd.oai.openapi"}
        x = self.session.get(
            "{PROTOCOL}://{HOSTNAME}:{PORT}/openapi/".format(
                PROTOCOL=env("PROTOCOL"),
                HOSTNAME=env("HOSTNAME"),
                PORT=env("PORT")
            )
        )
        self.openapi = yaml.load(x.text, Loader=yaml.FullLoader)
        self.session.headers = {"Accept" : "application/json"}
        self.user_urls = {}
        for user in self.session.get("{}://{}:{}/api/user/".format(env("PROTOCOL"), env("HOSTNAME"), env("PORT"))).json():
            self.user_urls[user["username"]] = user["url"]
        self.list_urls = {}
        for obj in self.openapi["components"]["schemas"].keys():
            actions = []
            for path, methods in self.openapi["paths"].items():
                path = "{}://{}:{}{}".format(env("PROTOCOL"), env("HOSTNAME"), env("PORT"), path)
                relevant = False
                for method, method_info in methods.items():
                    tags = method_info["tags"]
                    if obj.lower() in tags:
                        relevant = True
                        if method_info["operationId"].startswith("list") and not method_info["operationId"].startswith("list_"):
                            self.list_urls[obj] = path


            
    def action(self, action_name, url, data=None, expected=None, files={}):
        files = {k : open(v, "rb") if isinstance(v, str) else v for k, v in files.items()}
        resp = getattr(self.session, action_name)(url, data=data, files=files)
        return resp

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
