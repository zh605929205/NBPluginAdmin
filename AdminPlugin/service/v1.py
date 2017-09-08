#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from django.shortcuts import HttpResponse,render,redirect
from django.conf.urls import url,include
from django.urls import reverse
from django.http.request import QueryDict
from django.forms import ModelForm

class BaseYinGunAdmin(object):

    #用于app内所有数据库信息操作的生成

    list_display = "__all__"
    operate_model_form = None  #用以自定义显示

    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site
        self.request = None

        self.app_label = model_class._meta.app_label
        self.model_name = model_class._meta.model_name

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
            params = {
                "model":self.model_class,
                "fields":"__all__",
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

    def changelist_view(self,request):
        """
        查看列表
        :param request:
        :return:
        """
        #生成页面上：添加按钮
        self.request = request #当前请求信息

        param_dict = QueryDict(mutable=True) #获取 字典 对象，改成可修改的类型
        if request.GET: #如果有值
            param_dict["_changelistfilter"] = request.GET.urlencode() #就把获取到的传值原封不动的 写入queryset对象中
            # print(param_dict["_changelistfilter"]) #page=8&r=ooo urlencode()是把获取到的GET传值转换成url上可以应用的类型

        base_add_url = reverse("{0}:{1}_{2}_add".format(self.site.namespace,self.app_label,self.model_name)) #反向获取添加操作的url
        add_url = "{0}?{1}".format(base_add_url,param_dict.urlencode()) #把值传给添加url，携带用以返回当前目录
        # print(add_url)

        #生成页面上：表格
        result_list = self.model_class.objects.all() #从数据库中获取数据 对象列表
        context = {
            "result_list":result_list,
            "list_display":self.list_display,
            "ygadmin_obj":self,
            "add_url":add_url,
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
                model_form_obj.save() #保存到数据库
                base_list_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label, self.model_name))  # 反向获取添加操作的url
                list_url = "{0}?{1}".format(base_list_url, paras)  # 把值传给添加url，携带用以返回当前目录
                return redirect(list_url)
            else:
                #有错误信息
                pass
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
            model_form_obj = self.add_or_edit_modelform()(instance=obj)
        else:
            paras = request.GET.get("_changelistfilter")
            model_form_obj = self.add_or_edit_modelform()(data=request.POST,files=request.FILES,instance=obj)
            if model_form_obj.is_valid:
                model_form_obj.save()
                base_list_url = reverse("{0}:{1}_{2}_changelist".format(self.site.namespace, self.app_label,
                                                                        self.model_name))  # 反向获取添加操作的url
                list_url = "{0}?{1}".format(base_list_url, paras)  # 把值传给添加url，携带用以返回当前目录
                return redirect(list_url)
            else:
                pass
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

