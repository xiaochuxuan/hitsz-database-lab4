from django.contrib import admin

# Register your models here.
from .models import Laboratory, AcademicBuild, CompConfiguration, Software, Manager, Teacher, LaboratorySoftware

class AcademicBuild_Admin(admin.ModelAdmin):
    list_display = ['build_id', 'build_name', 'build_address']

class CompConfiguration_Admin(admin.ModelAdmin):
    list_display = ['conf_id', 'cpu', 'memory', 'gpu', 'mainboard']

class Software_Admin(admin.ModelAdmin):
    list_display = ['software_name', 'software_category', 'version', 'developer']

class Manager_Admin(admin.ModelAdmin):
    list_display = ['manager_id', 't_id', 'manager_name']

class Laboratory_Admin(admin.ModelAdmin):
    list_display = ['laboratory_id', 'manager_id', 'conf_id', 'build_id',
                    'laboratory_name', 'area', 'location', 'comp_sets']

class Teacher_Admin(admin.ModelAdmin):
    list_display = ['t_id', 't_name', 't_sex', 't_department']

class LaboratorySoftware_Admin(admin.ModelAdmin):
    list_display = ['software_name', 'laboratory_id']


admin.site.register(AcademicBuild, AcademicBuild_Admin)
admin.site.register(CompConfiguration, CompConfiguration_Admin)
admin.site.register(Software, Software_Admin)
admin.site.register(Manager, Manager_Admin)
admin.site.register(Laboratory, Laboratory_Admin)
admin.site.register(Teacher, Teacher_Admin)
admin.site.register(LaboratorySoftware, LaboratorySoftware_Admin)
