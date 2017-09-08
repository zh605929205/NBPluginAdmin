from django.db import models

# Create your models here.

class UserGroup(models.Model):
    title = models.CharField(max_length=32,verbose_name="分组名")

    def __str__(self):
        return self.title

class Role(models.Model):
    name = models.CharField(max_length=32,verbose_name="角色")

    def __str__(self):
        return self.name


class Users(models.Model):
    name = models.CharField(max_length=32,verbose_name="用户名")
    email = models.EmailField(max_length=32,verbose_name="邮箱")
    age = models.IntegerField(verbose_name="年龄")

    ug = models.ForeignKey(to=UserGroup,null=True,blank=True,verbose_name="用户组")
    rm = models.ManyToManyField(Role,verbose_name="角色")

    def __str__(self):
        return self.name