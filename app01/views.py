from django.shortcuts import render,redirect,HttpResponse
from app01 import models
# from django.forms import ModelForm
# from django.forms import fields
# from django.forms import widgets
#
# class TestForm(ModelForm):
#     class Meta:
#         pass

def test(request):
    user_group_list = models.UserGroup.objects.all()

    return render(request,"test.html",{"user_group_list":user_group_list})

def add_test(request):

    if request.method == "GET":
        return render(request,"add_test.html")

    else:
        popid = request.GET.get("popup")
        title = request.POST.get("title")
        if popid:
            obj = models.UserGroup.objects.create(title=title)
            return render(request,"popup_response.html",{"id":obj.id,"title":obj.title,"popid":popid})
        else:
            models.UserGroup.objects.create(title=title)
            return HttpResponse("重定向！")