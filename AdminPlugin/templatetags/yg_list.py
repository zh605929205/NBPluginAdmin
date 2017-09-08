#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from types import FunctionType
from django.template import Library

register = Library()

def table_head(list_display,ygadmin_obj):
    """
    生成表格头
    :param list_display:
    :param ygadmin_obj:
    :return:
    """
    if list_display == "__all__":
        yield "对象列表"
    else:
        for item in list_display:
            if isinstance(item, FunctionType):
                yield item(ygadmin_obj,is_header=True)
                # item = item.__name__.title() #查看函数名
                # item = item.__doc__.split(":",1)[0] #获取注释信息
            else:
                yield ygadmin_obj.model_class._meta.get_field(item).verbose_name

def table_body(result_list,list_display,ygadmin_obj):
    """
    生成表格中的内容
    :param result_list:
    :param list_display:
    :param ygadmin_obj:
    :return:
    """
    for row in result_list:
        if list_display == "__all__":
            yield [str(row),]
        else:
            yield [name(ygadmin_obj,row) if isinstance(name,FunctionType) else getattr(row,name) for name in list_display]

@register.inclusion_tag("yg/md.html")
def func(result_list,list_display,ygadmin_obj):

    v_head = table_head(list_display,ygadmin_obj)
    v_body = table_body(result_list,list_display,ygadmin_obj)

    return {"v_head":v_head,"xxx":v_body}
