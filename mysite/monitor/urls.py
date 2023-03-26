from django.urls import path
from . import views

app_name = 'monitor'
urlpatterns = [
    path('', views.index, name='index'),
    path('host_list', views.host_list, name='host_list'),
    path('<int:pk>/', views.HostDetailView.as_view(), name='host_detail'),
    path('login', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('host/', views.HostView.as_view(), name='host'),
    path('fullview/', views.FullViewHost.as_view(), name='fullview_host'),
    path('reload/', views.reload, name='reload'),
    path('reload_host/<host_id>', views.reload_host, name='reload_host'),
    path('addhost/', views.add_host, name='addhost'),
    path('search/', views.search_host, name='search_host'),
    path('searchfullview/', views.search_fullview_host, name='search_fullview_host'),
    path('update/<host_id>', views.update_host, name='update_host'),
    path('delete/<host_id>', views.delete_host, name='delete_host'),
    path('set_time/<time_id>', views.set_time, name='set_time'),
]
