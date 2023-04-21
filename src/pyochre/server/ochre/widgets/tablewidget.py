import logging
from django.conf import settings
from django.forms import Textarea, Widget
from pyochre.server.ochre.decorators import ochre_cache_method
from rdflib.namespace import RDF, RDFS, Namespace


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


logger = logging.getLogger(__name__)


@ochre_cache_method
def get_rows(value, widget):
    rows = {}
    for binding in value.query_properties(
            """
            SELECT ?row_name ?col_name ?val WHERE {{
              ?cell <{value_property}> ?val .
              ?cell ochre:partOf ?row .
              ?cell ochre:partOf ?col .
              ?row ochre:isA <{row_type}> .
              ?col ochre:isA <{column_type}> .
              ?row ochre:hasLabel ?row_name .
              ?col ochre:hasLabel ?col_name .
            }}
            """.format(
                value_property=widget.value_property,
                row_type=widget.row_type,
                column_type=widget.column_type
            )
    ):
        #print(binding)
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

    
class TableWidget(Widget):
    template_name = "ochre/template_pack/tabular.html"
    def __init__(
            self,
            props,
            # row_type,
            # row_ranked,
            # row_limit,
            # rows_sorted_by,
            # column_type,
            # column_ranked,
            # column_limit,
            # columns_sorted_by,
            # value_property,
            *argv,
            **argd
    ):
        print(props)
        self.row_type = props[OCHRE["hasRowType"]][0]
        self.row_ranked = props[OCHRE["isRowRanked"]][0]
        self.row_limit = props.get(OCHRE["hasRowLimit"], [None])[0]
        self.rows_sorted_by = props[OCHRE["hasRowsSortedBy"]][0]
        self.column_type = props[OCHRE["hasColumnType"]][0]
        self.column_ranked = props[OCHRE["isColumnRanked"]][0]
        self.column_limit = props.get(OCHRE["hasColumnLimit"], [None])[0]
        self.columns_sorted_by = props.get(OCHRE["hasColumnsSortedBy"], [None])[0]
        self.value_property = props[OCHRE["hasValueProperty"]][0]
        super(TableWidget, self).__init__(*argv, **argd)

        
    def get_context(self, name, value, attrs):
        context = super(TableWidget, self).get_context(name, value, attrs)
        rows, column_names = get_rows(value, self)
        context["widget"]["value"] = {
            "column_names" : [""] + column_names,
            "rows" : rows
        }
        return context
