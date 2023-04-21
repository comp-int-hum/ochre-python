import logging
import json
import os.path
from pyochre.utils import meta_open


logger = logging.getLogger(__name__)


def match(reference, candidate):
    return reference["model"] == candidate["model"] and all([candidate["object"][key] == value for key, value in reference["match"].items()])


def remove_satisfied(depends_on, satisfied):
    retval = []
    for reference in depends_on:
        matches = [other for other in satisfied if match(reference, other)]
        if len(matches) == 0:
            retval.append(reference)
    return retval


def contains(existing, reference):
    matches = [item for item in existing.get(reference["model"], []) if match(reference, {"model" : reference["model"], "object" : item})]
    return len(matches) > 0


def creation_order(unsatisfied, satisfied=[], existing={}):
    for i in range(len(unsatisfied)):
        unsatisfied[i]["depends_on"] = remove_satisfied(unsatisfied[i]["depends_on"], satisfied)

    still_unsatisfied = []

    for item in unsatisfied:
        if len(item["depends_on"]) == 0:
            satisfied.append(item)
        else:
            still_unsatisfied.append(item)

    if len(still_unsatisfied) == 0:
        return satisfied
    elif len(still_unsatisfied) == len(unsatisfied):
        deps = sum([item["depends_on"] for item in still_unsatisfied], [])
        if all([contains(existing, reference) for reference in deps]):
            return satisfied + unsatisfied
        else:
            raise Exception("Could not satisfy more dependencies, and they don't already exist in the system (or '--delete' was specified)")
    else:
        return creation_order(still_unsatisfied, satisfied, existing)


def create_plan(fixture_files, args, connection):
    existing = {}
    to_create = []
    for fixture_file in fixture_files:
        logger.info("Processing fixtures in '%s'", fixture_file)
        with meta_open(fixture_file, "rt") as ifd:
            for model, objs in json.loads(ifd.read()).items():
                if model in args.skip_models:
                    continue
                for obj in objs:                    
                    if "{}:{}".format(model, obj["name"]) not in args.skip_objects and model not in args.skip_models:
                        depends_on = []
                        for v in obj.values():
                            if isinstance(v, dict) and "model" in v:
                                depends_on.append(v)
                                existing[v["model"]] = existing.get(
                                    v["model"],
                                    connection.get_objects(v["model"])["results"]
                                )
                        to_create.append(
                            {
                                "model" : model,
                                "object" : obj,
                                "depends_on" : depends_on
                            }
                        )

    order = creation_order(
            [item for item in to_create if len(item["depends_on"]) > 0],
            [item for item in to_create if len(item["depends_on"]) == 0],
            existing
    )

    if args.delete:
       for model in set([item["model"] for item in order]):
           existing_items = connection.get_objects(model)["results"]
           logger.info("Deleting %d existing objects of model '%s'", len(existing_items), model)            
           for item in existing_items:
               connection.delete(item["url"])
    return order                


def perform_plan(plan, args, connection):
    for item in plan:
        obj = item["object"]
        model = item["model"]
        #if obj["name"] in args.skip_objects:
        #    logger.info("Skipping object '%s' of model '%s'", obj["name"], model)
        #    continue
        logger.info("Creating object '%s' of model '%s'", obj["name"], model)
        #existing[model] = existing.get(
        #    model,
        #    user.get(model_urls[model], follow_next=True)["results"]
        #)

        robj = {}
        files = {}
        #preexisting = [x for x in existing.get(model, []) if x["name"] == obj["name"]]
        #if args.replace:            
        #    for o in preexisting:
        #        logger.info("Deleting preexisting object '%s' of model '%s'", obj["name"], model)
        #        user.delete(o["url"])

        for k, v in obj.items():
            if isinstance(v, dict):
                if "model" in v:
                    # object-property lookup
                    #matches = [
                    #    x for x in user.get(model_urls[v["model"]], follow_next=True)["results"] if all(
                    #        [x[a] == b for a, b in v["match"].items()]
                    #    )
                    #]
                    #assert len(matches) == 1                            
                    #robj[k] = matches[0][v["field"]]
                    pass
                elif "filename" in v:
                    # file upload
                    for possible_path in reversed(args.file_paths):
                        possible_fname = os.path.join(possible_path, v["filename"])
                        if os.path.exists(possible_fname):
                            files[k] = (
                                v["filename"],
                                open(possible_fname, "rb"),
                                v["content_type"]
                            )
                    if k not in files:
                        raise Exception("Could not find file '{}' in any of the directories {}".format(v["filename"], args.file_paths))
            else:
                # standard key-value
                robj[k] = v
        print(model, robj, files)
        
        connection.create(model, robj, files=files)
