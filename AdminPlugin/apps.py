from django.apps import AppConfig


class AdminpluginConfig(AppConfig):
    name = 'AdminPlugin'

    def ready(self):
        super(AdminpluginConfig,self).ready()

        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules("yg")