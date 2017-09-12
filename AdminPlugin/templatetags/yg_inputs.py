#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from django.template import Library
from django.forms.boundfield import BoundField
from django.forms.models import ModelChoiceField
from django.urls import reverse
from AdminPlugin.service import v1

register = Library()

def infos(form):

    for item in form:

        row = {"is_popup":False,"item":None,"popup_url":None}
        if isinstance(item.field,ModelChoiceField) and item.field.queryset.model in v1.site._registry:
            # print(item.field.queryset.model)
            target_app_label = item.field.queryset.model._meta.app_label
            target_model_name = item.field.queryset.model._meta.model_name
            url_name = "{0}:{1}_{2}_add".format(v1.site.namespace,target_app_label,target_model_name)
            target_url = "{0}?popup={1}".format(reverse(url_name), item.auto_id)

            row["is_popup"] = True
            row["item"] = item
            row["popup_url"] = target_url
        else:
            row["item"] = item

        yield row

@register.inclusion_tag("yg/inputs.html")
def func(form):
    inputs = infos(form)
    return {"inputs":inputs}

