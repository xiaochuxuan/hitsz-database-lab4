from django.urls import path, include

import management.views

# 配置路由
urlpatterns = [
    path('', management.views.index, name='management_home'),
    path('laboratory_view', management.views.laboratory_view, name='laboratory_list'),
    path('reserve_view/<laboratory_name>/', management.views.reserve_view, name='reserve'),
    path('manage_view', management.views.manage_view, name='manage_laboratory'),
    path('reservation_manage_view', management.views.reservation_manage_view, name='reservation_manage'),
    path('pass_reservation/<record_id>/', management.views.pass_reservation, name='pass_reservation'),
    path('update_conf/<laboratory_name>/', management.views.update_conf, name='update_conf'),
    path('add_software', management.views.add_software, name='add_software'),
    path('add_software_laboratory/<laboratory_name>/<software_name>/', management.views.add_software_laboratory, name='add_software_laboratory'),
    path('reservation_query_view', management.views.reservation_query_view, name='reservation_query'),
    path('delete_reservation/<record_id>/', management.views.delete_reservation, name='delete_reservation'),
    path('laboratory_occupancy_view/<laboratory_name>/', management.views.laboratory_occupancy_view, name='laboratory_occupancy'),
    path('info_view', management.views.info_view, name='user_info'),

]
