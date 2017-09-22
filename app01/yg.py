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
            tag = "<input name='pk' type='checkbox' value='{0}'>".format(obj.pk)
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

    def initial(self,request):
        """

        :param request:
        :return: True 当前页面不动;False跳转
        """
        pk_list = request.POST.getlist("pk")
        models.Users.objects.filter(pk__in=pk_list).update(name="赵四")
        return True
    initial.text = "初始化"

    def multi_del(self,request):
        pass
    multi_del.text = "批量删除"
    action_list = [initial,multi_del]
    list_display = [checkbox,"id","name","email","age",comb,func] #自定义要显示的列名或方法

    from AdminPlugin.utils.filter_code import FilterOption

    def email(self, option, request):
        """
        名字必须和数据库字段名一致
        自定义字段处理函数，必须返回一个FilterList对象
        :param option:  FilterOption对象
        :param request: 请求信息
        :return:
        """
        from AdminPlugin.utils.filter_code import FilterList
        queryset = models.Users.objects.filter(id__gt=2) #自定义获取数据信息
        return FilterList(option, queryset, request)
    #利用 FilterOption 类封装的多个对象
    filter_list = [
        FilterOption("name", False, text_func_name="text_username", val_func_name="value_username"),
        FilterOption("email", False, text_func_name="text_email", val_func_name="value_email"),
        FilterOption("age", False, text_func_name="text_age", val_func_name="value_age"),
        FilterOption("ug", True),
        FilterOption("rm", True),
    ]

class YinGunRole(v1.BaseYinGunAdmin):
    list_display = ["id","name"]

v1.site.register(models.Users,YinGunUserInfo)
v1.site.register(models.Role,YinGunRole)
v1.site.register(models.UserGroup,)

