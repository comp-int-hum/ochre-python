import logging
from collections import OrderedDict
from django import template
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import get_perms
from pyochre.server.ochre.renderers import OchreHTMLFormRenderer
from pyochre.server.ochre.models import Documentation
from pyochre.server.ochre.serializers import DocumentationSerializer


logger = logging.getLogger(__name__)


register = template.Library()


@register.simple_tag(takes_context=True)
def ochre_render_form(
        context,
        serializer,
        template_pack=None,
        mode="view",
        uid=None
):
    try:
        style = {'template_pack': template_pack} if template_pack else {}
        args = {}        
        for name in ["uid"]:
            if name in context:
                args[name] = context[name]
        renderer = OchreHTMLFormRenderer()
        try:
            style["object_id"] = serializer.data.get("id", None)
        except:
            style["object_id"] = None
        tab_view = mode == "view" and hasattr(serializer, "Meta") and getattr(serializer.Meta, "tab_view", False)
        keep = getattr(serializer.Meta, "{}_fields".format(mode), None) if hasattr(serializer, "Meta") else None
        if keep:
            serializer.fields = {
                field_name : field for field_name, field in serializer.fields.items() if field_name in keep
            }
        for i, field in enumerate(serializer.fields):
            serializer.fields[field].style["index"] = i
            if mode in ["edit", "create"]:
                serializer.fields[field].style["editable"] = True
        return renderer.render(
            serializer.data,
            None,
            {
                'uid' : uid,
                'style': style,
                "mode" : mode,
                "tab_view" : tab_view,
                "request" : context.get("request")
            }
        )
    except Exception as e:
        logger.info("Exception: %s", e)
        raise e


@register.simple_tag(takes_context=True)
def ochre_get_documentation_object(context, view_name, item):    
    if isinstance(item, (str, dict)):
        referent_type = None
        referent_id = None
    elif item.is_model() and not item.is_object():
        referent_type = ContentType.objects.get_for_model(item)
        referent_id = None
    elif item.is_object():
        referent_type = ContentType.objects.get_for_model(item._meta.model)
        referent_id = item.id
    else:
        logger.error("Something strange: %s", item)
        referent_type = None
        referent_id = None
    referent_id = referent_id if referent_id else 0
    logger.info(
        "Retrieving documentation for view/model/object '%s/%s/%s'",
        view_name,
        referent_type,
        referent_id
    )        
    referent_type_id = referent_type.id if referent_type else None
    docs = Documentation.objects.filter(
        view_name=view_name,
        referent_type=referent_type,
        referent_id=referent_id
    )
    ret_obj = docs[0] if len(docs) > 0 else None
    if ret_obj:
        ret_ser = DocumentationSerializer(ret_obj, context=context)
        can_edit = Documentation.get_add_perm() in get_perms(
            context["request"].user,
            ret_obj
        )
    else:
        logger.info("No such documentation, will create a new entry")
        data = {
            "view_name": view_name,
            "referent_type" : referent_type_id,
            "referent_id" : referent_id,
            "name" : "_".join(
                [
                    str(x) for x in
                    [
                        view_name,
                        referent_type_id,
                        referent_id
                    ] if x
                ]
            )
        }
        ret_ser = DocumentationSerializer(data=data, context=context)
        ret_ser.is_valid()
        can_edit = Documentation.get_add_perm() in get_perms(
            context["request"].user,
            Documentation
        )
    retval = {
        "object" : ret_obj if ret_obj else Documentation(
            name="_".join(
                [
                    str(x) for x in
                    [
                        view_name,
                        referent_type_id,
                        referent_id
                    ] if x
                ]
            ),
            view_name=view_name,
            referent_type=referent_type,
            referent_id=referent_id,
        ),
        "can_edit" : can_edit,
        "serializer" : ret_ser
    }
    return retval
