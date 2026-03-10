"""ssccbproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from userapp import views as user_views
from adminapp import views as admin_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',user_views.Home,name='home'),
    path('about',user_views.About,name='about'),
    path('contact',user_views.Contact,name='contact'),
    path('Admin_login',user_views.Admin_login,name='Admin_login'),
    path('User_register',user_views.User_register,name='User_register'),
    path('login',user_views.User_login,name='login'),
    
    
    path('User_index',user_views.User_index,name='User_index'),
    path('User_about',user_views.User_about,name='User_about'),
    path('upload_files',user_views.Upload_files,name='upload_files'),
    path('myfiles',user_views.Myfiles,name='myfiles'),
    path('My_profile',user_views.Admin_login2,name='Admin_login2'),
    path('file/<int:id>',user_views.filedownload,name='userdownload'),
    path('publicfile/<int:id>',user_views.public_download,name='public'),
    path('Admin_login2',user_views.Myprofile,name='My_profile'),
    #admin
    path('admin_dashboard',admin_views.admin_dashboard,name='admin_index'),
    path('admin_cmastatus',admin_views.admin_cmastatus,name='admin_cmastatus'),
    path('admin_userrequest',admin_views.admin_userrequest,name='admin_userrequest'),
    path('user_accept/<int:id>/',admin_views.user_accept,name='user_accept'),
    path('user_reject/<int:id>/',admin_views.user_reject,name='user_reject'),
    # path('',admin_views.,name=''),
    # path('',admin_views.,name=''),    
    # path('',admin_views.,name=''),
    # Warning please keep these two urls at last only you can write new urls above only
    path('url/<int:id>',user_views.Make,name='Make'),
    path('<str:token>', user_views.shortlink, name='shortlink'),
    
]
urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

