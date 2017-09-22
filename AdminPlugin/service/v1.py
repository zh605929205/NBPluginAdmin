#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import copy

from django.conf.urls import url,include
from django.forms import ModelForm
from django.forms import widgets
from django.http.request import QueryDict
from django.shortcuts import HttpResponse,render,redirect
from django.urls import reverse


class BaseYinGunAdmin(object):

    #用于app内所有数据库信息操作的生成

    list_display = "__all__"
    action_list = [] #用于定制action操作的列表
    operate_model_form = None  #用以自定义显示
    filter_list = []  #用于组合筛选的列表

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site
        self.request = None

        self.app_label = model_class._meta.app_label
        self.model_name = model_class._meta.model_name

    """2. 定制列表中的筛选条件"""
    def get_model_field_name_list(self):
        """
        获取当前model中定义的字段
        :return:
        """
        # print(type(self.model_class._meta))
        from django.db.models.options import Options
        return [item.name for item in self.model_class._meta.fields]

    def get_model_field_name_list_m2m(self):
        return [item.name for item in self.model_class._meta.many_to_many]

    def get_all_model_field_name_list(self):
        """
        # 获取当前model中定义的字段（包括反向查找字段）
        :return:
        """
        return [item.name for item in self.model_class._meta._get_fields()]

    def get_change_list_condition(self, query_params):

        # 获取当前访问的数据类 self.model_class
        field_list = self.get_all_model_field_name_list()
        condition = {}
        for k in query_params:
            if k not in field_list:
                # raise Exception('条件查询字段%s不合法，合法字段为：%s' % (k, ",".join(field_list)))
                continue
            condition[k + "__in"] = query_params.getlist(k)
        return condition

    def add_or_edit_modelform(self):
        """
        定义获取数据及页面显示的函数
        :return:
        """
        if self.operate_model_form:
            return self.operate_model_form
        else:
            # class MyModelForm(ModelForm):
            #     class Meta:
            #         model = self.model_class
            #         fields = "__all__"
            s = self.model_class._meta.fields

            error_msg = {}
            # wid = {}
            # for i in s:
            #     error_msg[i.name] = {'required':'内容不能为空','invalid':'格式错误'}
            #     if i.name == "ug":
            #          ww = widgets.Select(attrs={"class":"form-control"},)
            #     else:
            #         ww = widgets.TextInput(attrs={"class":"form-control"},)
            #     wid[i.name] =ww
            # #未解决
            params = {
                "model":self.model_class,
                "fields":"__all__",
                "error_messages":error_msg,
                # "widgets":wid,
            }

            _m = type("Meta",(object,),params)
            MyModelForm = type("MyModelForm",(ModelForm,),{"Meta":_m})
            return MyModelForm
    @property
    def urls(self):
        """
        生成增删改查的url
        :return:
        """
        info = self.model_class._meta.app_label,self.model_class._meta.model_name
        urlpatterns = [
            url(r'^$', self.changelist_view, name='%s_%s_changelist' % info),
            url(r'^add/$', self.add_view, name='%s_%s_add' % info),
            url(r'^(.+)/delete/$',self.delete_view, name='%s_%s_delete' % info),
            url(r'^(.+)/change/$', self.change_view, name='%s_%s_change' % info),
        ]
        return urlpatterns

    def another_urls(self):
        """
        钩子函数，用于自定义额外的URL
        :return:
        """
        return []

    def changelist_view(self,request):
        """
        查看列表
        :param request:
        :return:
        """
        #生成页面上：添加按钮
        self.request = request #当前请求信息
        result_lists = self.model_class.objects.filter(**self.get_change_list_condition(request.GET))

        param_dict = QueryDict(mutable=True) #获取 字典 对象，改成可修改的类型
        if request.GET: #如果有值
            param_dict["_changelistfilter"] = request.GET.urlencode() #就把获取到的传值原封不动的 写入queryset对象中
            # print(param_dict["_changelistfilter"]) #page=8&r=ooo urlencode()是把获取到的GET传值转换成url上可以应用的类型

        base_add_url = reverse("{0}:{1}_{2}_add".format(self.site.namespace,self.app_label,self.model_name)) #反向获取添加操作的url
        add_url = "{0}?{1}".format(base_add_url,param_dict.urlencode()) #把值传给添加url，携带用以返回当前目录
        # print(add_url)

        #分页 开始
        # condition = {}
        from AdminPlugin.utils.my_page import PageInfo
        # all_count = self.model_class.objects.filter(**condition).count()

        all_count = result_lists.count()
        base_page_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace,self.app_label,self.model_name)) #反向获取操作的url
        page_param_dict = copy.deepcopy(request.GET)  #获取页面 URL GET方式传入的参数
        page_param_dict._mutable = True #可更改

        page_obj = PageInfo(request.GET.get("page"),all_count,base_page_url,page_param_dict)
        #获取数据生成页面上：表格
        result_list = result_lists[page_obj.start:page_obj.end] #从数据库中获取数据 对象列表
        #分页结束

        ######Action操作####
        #get请求，显示下拉框
        action_list = []
        for item in self.action_list:
            tpl = {"name":item.__name__,"text":item.text}
            action_list.append(tpl)
        if request.method == "POST":
            #1、获取action
            func_name_str = request.POST.get("action")
            ret = getattr(self,func_name_str)(request)
            action_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace,self.app_label,self.model_name)) #反向获取添加操作的url
            if ret:
                action_url = "{0}?{1}".format(action_url,request.GET.urlencode())
            return redirect(action_url)

        # ############ 组合搜索操作 ##############
        from AdminPlugin.utils.filter_code import FilterList

        filter_list = [] #先定义一个空列表，用于存放处理之后的信息
        for option in self.filter_list:#循环列表，获取每个FilterOption对象
            if option.is_func: #调用对象下的 is_func方法，判断是否传入的第一个参数是否为函数
                data_list = option.field_or_func(self, option, request) #如果是函数，就把当前对象，请求信息交给该函数处理
            else:#不是函数，那就是字段
                from django.db.models import ForeignKey, ManyToManyField #用于验证
                field = self.model_class._meta.get_field(option.field_or_func) #通过对象中传入的field_or_func参数，获取对应数据库中的field对象
                #获取关联表的数据
                if isinstance(field, ForeignKey): #判断字段类型，如果是外键或是字符串
                    # print(field.rel.model) # ug       -> UserGroup表
                    #把当前FilterOption对象，对应的数据库数据，request请求传递给FilterList类，实例化得到一个对应的对象
                    data_list = FilterList(option, field.rel.model.objects.all(), request)
                elif isinstance(field, ManyToManyField):#判断时候是多对多类型的字段
                    # print(field.rel.model) # rm      -> Role表
                    data_list = FilterList(option, field.rel.model.objects.all(), request)
                else:
                    # print(field.model, self.model_class)
                    #以上都不满足的话，就直接获取自己表的数据
                    data_list = FilterList(option, field.model.objects.all(), request)
            filter_list.append(data_list) #把实例化的 FilterList 对象添加到列表中，传递给前端

        context = {
            "result_list":result_list,
            "list_display":self.list_display,
            "ygadmin_obj":self,
            "add_url":add_url,
            "page_str":page_obj.pager,
            "action_list":action_list,
            "filter_list":filter_list,
        }

        return render(request, "yg/change_list.html",context)

    def add_view(self,request):
        """
        添加数据
        :param request: 请求信息
        :return:
        """
        if request.method == "GET":
            model_form_obj = self.add_or_edit_modelform()() #form组件，直接返回页面
        else:
            #POST请求  form组件中传入返回的参数，以在数据库中添加
            paras = request.GET.get("_changelistfilter")
            model_form_obj = self.add_or_edit_modelform()(data=request.POST,files=request.FILES)
            if model_form_obj.is_valid():#验证
                #验证成功保存到数据库及跳转到查询页
                obj = model_form_obj.save() #保存到数据库
                popid = request.GET.get("popup") #获取添加操作时，url传回的值
                # 如果是popup 弹窗添加的话 就执行这个
                if popid:
                    return render(request,"yg/popup_response.html",{'data_dict':{ 'pk': obj.pk,'text':str(obj),'popid':popid}})
                #如果是页面直接url访问
                else:
                    base_list_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))  # 反向获取添加操作的url
                    list_url = "{0}?{1}".format(base_list_url, paras)  # 把值传给添加url，携带用以返回当前目录
                    return redirect(list_url)

        context = {
            "form":model_form_obj,
        }

        return render(request,"yg/add.html",context)

    def delete_view(self,request,pk):
        """
        删除
        :param request:
        :return:
        """
        self.model_class.objects.filter(pk=pk).delete()
        paras = request.GET.get("_changelistfilter")
        base_list_url = reverse(
            "{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))  # 反向获取添加操作的url
        list_url = "{0}?{1}".format(base_list_url, paras)  # 把值传给添加url，携带用以返回当前目录
        return redirect(list_url)

    def change_view(self,request,pk):
        """
        更改
        :param request:
        :return:
        """
        # 1. 获取_changelistfilter中传递的参数
        # request.GET.get("_changelistfilter")
        # 2. 页面显示并提供默认值ModelForm
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse("ID不存在")
        if request.method == "GET":
            model_form_obj = self.add_or_edit_modelform()(instance=obj)#传入默认值，instance
        else:
            paras = request.GET.get("_changelistfilter")
            model_form_obj = self.add_or_edit_modelform()(data=request.POST,files=request.FILES,instance=obj) #若想修改，必须有原始的值
            if model_form_obj.is_valid:
                model_form_obj.save() #保存数据，没有初始值就会创建一条数据，有初始值的话会完成修改
                base_list_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label,
                                                                        self.model_name))  # 反向获取添加操作的url
                list_url = "{0}?{1}".format(base_list_url, paras)  # 把值传给添加url，携带用以返回当前目录
                return redirect(list_url)

        # 3. 返回页面
        context = {
            "form": model_form_obj,
        }

        return render(request, "yg/edit.html", context)

class YinGunSite(object):
    def __init__(self):
        self._registry = {}
        self.namespace = "yingun"
        self.app_name = "yingun"

    def register(self,model_class,xxx=BaseYinGunAdmin):
        """
        注册执行
        :param model_class:  数据库表名
        :param xxx:  #处理参数的类
        :return:
        """
        self._registry[model_class] = xxx(model_class,self)

    def get_urls(self):
        """
        生成初步的url
        :return:
        """
        ret = [
            url(r"^login/",self.login,name="login"),
            url(r"^logout/",self.logout,name="logout"),
        ]
        for model_cls,admin_obj in self._registry.items():
            app_label = model_cls._meta.app_label #app项目名
            model_name = model_cls._meta.model_name #小写数据库表名
            ret.append(url(r'%s/%s/' % (app_label, model_name),include(admin_obj.urls))) #路由分发

        return ret

    @property
    def urls(self):
        """
        urls注册生成url
        namespace 是为了避免冲突
        :return:
        """
        return self.get_urls(),self.app_name,self.namespace

    def login(self,request):
        return HttpResponse("login")

    def logout(self,request):
        return HttpResponse("logout")

site = YinGunSite()

