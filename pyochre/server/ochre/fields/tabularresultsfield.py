import logging
from secrets import token_hex as random_token
from rest_framework.serializers import Field
from jsonpath import JSONPath


logger = logging.getLogger(__name__)


class TabularResultsField(Field):

    def __init__(self, property_field, *argv, **argd):
        self.value_format = argd.pop("value_format", "{0}")
        self.property_field_args = argd.pop("property_field_args", {})
        for param in ["row_names_path", "column_names_path", "row_label_path", "column_label_path", "lookup_path", "rows_path"]:
            val = argd.pop(param, None)
            setattr(self, param, JSONPath(val) if val else None)
        retval = super(TabularResultsField, self).__init__(*argv, **argd)
        self.style["property_field"] = property_field        
        self.style["base_template"] = "tabular.html"
        self.style["template_pack"] = "ochre/template_pack"
        self.style["id"] = "prefix_{}".format(random_token(8))
        self.style["value_id"] = "value_{}".format(self.style["id"])
        self.style["spec_id"] = "spec_{}".format(self.style["id"])
        self.style["div_id"] = "div_{}".format(self.style["id"])
        self.style["editable"] = True
        self.field_name = "tabular_{}".format(random_token(6))
        return retval

    def get_default_value(self):
        j = getattr(self.style["object"], self.style["property_field"])(**self.property_field_args)
        retval = {}
        for param in ["row_names_path", "column_names_path", "row_label_path", "column_label_path", "lookup_path", "rows_path"]:
            val = getattr(self, param, None)
            if val:
                retval[param] = val.parse(j)[0]
        retval["rows"] = []
        for row in retval["rows_path"]: #self.rows_path.parse(j)[0]:            
            if retval.get("lookup_path", None):
                item = []
                for col_name in retval["lookup_path"]:
                    item.append(self.value_format.format(row[col_name]) if col_name in row else "")
            else:
                item = [self.value_format.format(v) for v in row]
            retval["rows"].append(item)
        return retval
