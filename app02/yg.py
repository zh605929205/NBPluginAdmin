#!/usr/bin/env python
# _*_ coding:utf-8 _*_
from AdminPlugin.service import v1
from app02 import models

v1.site.register(models.XX)
v1.site.register(models.OO)

