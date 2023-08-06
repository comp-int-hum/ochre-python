import logging
from secrets import token_hex as random_token
from rest_framework.serializers import Field
from pyochre.server.ochre.decorators import ochre_cache_method


logger = logging.getLogger(__name__)


def get_rows(value, widget):
    rows = {}
    for binding in value.query_properties(
            """
            SELECT ?row_name ?col_name ?val WHERE {{
              ?cell <{value_property}> ?val .
              ?cell ochre:partOf ?row .
              ?cell ochre:partOf ?col .
              ?row ochre:instanceOf <{row_type}> .
              ?col ochre:instanceOf <{column_type}> .
              ?row ochre:hasLabel ?row_name .
              ?col ochre:hasLabel ?col_name .
            }}
            """.format(
                value_property=widget.value_property,
                row_type=widget.row_type,
                column_type=widget.column_type
            )
    ):
        rn = binding.get("row_name") #["value"]
        cn = binding.get("col_name") #["value"]
        v = binding.get("val") #(float if binding.get("val", {}).get("datatype", "").endswith("float") else str)(binding.get("val"))
        rows[rn] = rows.get(rn, [])
        rows[rn].append((v, cn))
    if widget.column_ranked:            
        rows = [
            [rn] + ["{}:{:.03}".format(cn, float(v)) for i, (v, cn) in enumerate(sorted(cols, reverse=True))
                    if not widget.column_limit or i < widget.column_limit.value]
            for rn, cols in rows.items()
        ]
        column_names = ["{}".format(i + 1) for i in range(widget.column_limit.value)]
    else:
        rows = {
            rn : {k : v for k, v in cols.items()}
            for rn, cols in rows.items()
        }
    return (rows, column_names)


class TableField(Field):
    
    def __init__(self, *argv, **argd):
        super(
            TableField,
            self
        ).__init__(
            source="*",
            required=False,
            label=argd.get("label", "")
        )
        self.field_name = "interaction_{}".format(random_token(6))
        self.style["template_pack"] = "ochre/template_pack"
        self.style["base_template"] = "tabular.html"

        self.row_type = argd.get("row_type", None)
        self.row_ranked = argd.get("row_ranked", None)
        self.row_limit = argd.get("row_limit", None)
        self.rows_sorted_by = argd.get("rows_sorted_by", None)
        
        self.column_type = argd.get("column_type", None)
        self.column_ranked = argd.get("column_ranked", None)
        self.column_limit = argd.get("column_limit", None)
        self.columns_sorted_by = argd.get("columns_sorted_by", None)
        self.value_property = argd.get("value_property", None)

    @ochre_cache_method
    def to_representation(self, value):
        rows, column_names = get_rows(value, self)
        retval = {
            "column_names" : [""] + column_names,
            "rows" : rows
        }
        return retval
