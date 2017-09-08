#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from AdminPlugin.service import v1
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http.request import QueryDict
from app01 import models

class YinGunUserInfo(v1.BaseYinGunAdmin):

    def func(self,obj=None,is_header=False):
        """
        操作
        :param obj:
        :return:
        """
        # 当前app名称
        # 当前model名称
        # namespace名称
        # name = namespace:app名称_model名称_change
        if is_header:
            return "操作"
        else:
            # name = "{0}:{1}_{2}_change".format(self.site.namespace,self.model_class._meta.app_label,self.model_class._meta.model_name)
            # url = reverse(name,args=(obj.pk,))
            param_dict = QueryDict(mutable=True)  # 获取 字典 对象，改成可修改的类型
            if self.request.GET:  # 如果有值
                param_dict["_changelistfilter"] = self.request.GET.urlencode()  # 就把获取到的传值原封不动的 写入queryset对象中

            base_edit_url = reverse("{0}:{1}_{2}_change".format(self.site.namespace, self.app_label, self.model_name),
                                    args=(obj.pk,))  # 反向获取添加操作的url
            base_del_url = reverse("{0}:{1}_{2}_delete".format(self.site.namespace, self.app_label, self.model_name),
                                   args=(obj.pk,))  # 反向获取添加操作的url

            edit_url = "{0}?{1}".format(base_edit_url, param_dict.urlencode())  # 把值传给添加url，携带用以返回当前目录
            del_url = "{0}?{1}".format(base_del_url, param_dict.urlencode())  # 把值传给添加url，携带用以返回当前目录

            return mark_safe("<a href='{0}'>编辑</a> | <a href='{1}'>删除</a>".format(edit_url, del_url))

    def checkbox(self,obj=None,is_header=False):
        """
        在页面上显示 多选框
        :param obj:
        :return:
        """
        if is_header:
            return "选项"
        else:
            tag = "<input type='checkbox' value='{0}'>".format(obj.pk)
            return mark_safe(tag)

    def comb(self,obj=None,is_header=False):
        """
        定制某列的函数
        :param obj: 对象 数据库
        :param is_header:
        :return:
        """
        if is_header:
            return "聚合某列"
        else:
            return "%s-%s"%(obj.name,obj.age,)

    list_display = [checkbox,"id","name","email","age",comb,func] #自定义要显示的列名或方法

class YinGunRole(v1.BaseYinGunAdmin):
    list_display = ["id","name"]

v1.site.register(models.Users,YinGunUserInfo)
v1.site.register(models.Role,YinGunRole)

