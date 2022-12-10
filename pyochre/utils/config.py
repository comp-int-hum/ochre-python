import os.path
import os
import stat
import logging
import json


logger = logging.getLogger(__name__)
# st_mode, st_uid, st_gid chmod fchmod
# more checks
# os.fstat(ofd.fileno())

class Config(dict):

    def __init__(self, mode="r", ochre_path="~/.ochre", conf_file="~/.ochre/config.json", **argd):
        self.mode = mode
        self.ochre_path = os.path.expanduser(ochre_path)
        self.conf_file = os.path.expanduser(conf_file)
        if not os.path.exists(self.ochre_path):
            logger.info("Creating OCHRE directory '%s'", self.ochre_path)
            os.mkdir(self.ochre_path)
            os.mkdir(os.path.join(self.ochre_path, "cache"))
            os.mkdir(os.path.join(self.ochre_path, "temp"))
        elif not os.path.isfile(self.conf_file):
            logger.info(
                "The configuration file '%s' either doesn't exist, or isn't a file.  Starting with an empty configuration.",
                self.conf_file
            )
        else:
            if os.path.exists(self.conf_file):
                with open(self.conf_file, "rt") as ifd:
                    for k, v in json.loads(ifd.read()).items():
                        self[k] = v
        for k, v in argd.items():
            if v:
                self[k] = v        

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if "w" in self.mode and self.conf_file:
            with open(self.conf_file, "wt") as ofd:
                ofd.write(json.dumps({k : v for k, v in self.items() if k != "func"}, indent=4))
            os.chmod(self.conf_file, stat.S_IWUSR|stat.S_IRUSR)
