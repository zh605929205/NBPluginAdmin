import copy
from types import FunctionType
from django.utils.safestring import mark_safe

class FilterOption(object):
    def __init__(self, field_or_func, is_multi=False, text_func_name=None, val_func_name=None):
        """
        :param field: 字段名称或函数
        :param is_multi: 是否支持多选
        :param text_func_name: 在Model中定义函数，显示文本名称，默认使用 str(对象)
        :param val_func_name:  在Model中定义函数，显示文本名称，默认使用 对象.pk
        """
        self.field_or_func = field_or_func
        self.is_multi = is_multi
        self.text_func_name = text_func_name
        self.val_func_name = val_func_name

    @property
    def is_func(self):
        """
        判断传入的 field_or_func 参数是否为函数
        :return:
        """
        if isinstance(self.field_or_func, FunctionType):
            return True

    @property
    def name(self):
        """
        获取字段或是函数的名字
        :return:
        """
        if self.is_func:
            return self.field_or_func.__name__
        else:
            return self.field_or_func


class FilterList(object):
    def __init__(self,option,queryset,request):
        """

        :param option:
        :param queryset: 数据库中获取的models数据
        :param request: GET请求的所有信息
        """
        self.option = option  #FilterOption类的一个对象
        self.queryset = queryset #对应的获取的数据集信息
        self.param_dict = copy.deepcopy(request.GET)  #request传值 querydict字典类型
        self.path_info = request.path_info  #获取当前访问的url地址

    def __iter__(self):

        #定制全部 按钮
        yield mark_safe("<div class='all-area'>")

        #如果GET传参有以当前字段名字命名的传参，那就取消全局的样式；没有的话就是全部
        if self.option.name in self.param_dict: #判断操作的名字在不在GET传参中
            pop_val = self.param_dict.pop(self.option.name)
            url = "{0}?{1}".format(self.path_info, self.param_dict.urlencode())
            self.param_dict.setlist(self.option.name,pop_val) #再把之前的值，重新写回querydict中
            yield mark_safe("<a href='{0}'>全部</a>".format(url))
        else:
            url = "{0}?{1}".format(self.path_info,self.param_dict.urlencode())
            yield mark_safe("<a class='active' href='{0}'>全部</a>".format(url))
        yield mark_safe("</div><div class='others-area'>")

        #定制 过滤条件按钮
        for row in self.queryset: #对从数据库获取的数据进行循环，获取每个对象
            param_dict = copy.deepcopy(self.param_dict) #获取GET请求 传参 循环进来做一次深拷贝
            val = str(getattr(row,self.option.val_func_name)() if self.option.val_func_name else row.pk) #获取对应对象的值
            text = getattr(row,self.option.text_func_name)() if self.option.text_func_name else str(row) #获取从数据中获取对应对象的文本信息
            # self.param_dict   --->  username=fangshaowei&ug=1&email=666
            active = False #定义标志位
            value_list = param_dict.getlist(self.option.name)  # 获取对应字段name的 get传参列表
            # print(value_list)
            #判断是多选
            if self.option.is_multi:
                if val in value_list: #如果再次选择的参数存在GET传参的列表中
                    value_list.remove(val) # 就把这个值删除
                    param_dict.setlist(self.option.name,value_list)#重新赋值
                    active = True #更改标志位的状态
                else:
                    param_dict.appendlist(self.option.name,val) #如果不存在就把这个值添加到对应名字的values中
            #单选
            else:
                if val in value_list: # 如果传参的值在列表内，说明又点了一次，状态不变
                    active = True
                param_dict[self.option.name] = val #否则的话就直接赋值，会自动把值转成列表传入(1个无所谓)

            url = "{0}?{1}".format(self.path_info, param_dict.urlencode()) #拼接得到的新的url地址，包括url和GET传参
            #标志位判断，用于修改选中的动作
            if active:
                tpl = "<a class='active' href='{0}'>{1}</a>".format(url,text)
            else:
                tpl = "<a href='{0}'>{1}</a>".format(url, text)
            yield mark_safe(tpl)

        yield mark_safe("</div>")