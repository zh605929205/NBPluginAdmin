#!/usr/bin/env python
# _*_ coding:utf-8 _*_

class FilterList(object):
    def __init__(self,option,data_list):
        self.option = option
        self.data_list = data_list

    def show(self):
        self.option.nick()

    def __iter__(self):
        yield "全部："
        for i in self.data_list:
            yield "<a href='{0}'>{1}</a>".format(i,self.option.bs+i)

class FilterOption(object):

    def __init__(self,name,age):
        self.name = name
        self.age = age

    def nick(self):
        tpl = self.name + str(self.age)
        return tpl
    @property
    def bs(self):
        if self.age > 15:
            return "大"
        else:
            return "小"
obj_list = [

    FilterList(FilterOption("你好",19),["怒人","绿巨人"]),
    FilterList(FilterOption("好人",12),["女人","绿巨人"]),
    FilterList(FilterOption("好嘞",18),["男人","绿巨人"]),
    FilterList(FilterOption("好不",14),["伪人","绿巨人"]),
]

for obj in obj_list:
    for item in obj:
        print(item,end="   ")
    else:
        print("")

