#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from django.template import Library
from django.forms.boundfield import BoundField
register = Library()

def infos(form,ygadmin_obj):
    for item in form:
        nm = ygadmin_obj.model_class._meta.get_field(item.name).verbose_name  #字段名
        # print("name:",nm)
        # print("obj:",item.field) #form组件对象
        yield [nm,item]

@register.inclusion_tag("yg/inputs.html")
def func(form,ygadmin_obj):
    inputs = infos(form,ygadmin_obj)
    return {"inputs":inputs}

