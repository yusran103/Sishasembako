"""pasar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from sishasembapo import views as pasar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login', pasar.Login, name="login"),
    path('', pasar.index, name="index"),
    path('logout', pasar.Logout, name="logout"),
    # CHANGE PASSWORD
    path('changepassword/<int:pk>', pasar.changepassword , name='changepassword'),
    path('changeprofile/<int:pk>', pasar.changeprofile, name='changeprofile'),
    path('harga', pasar.view_harga , name='list_harga_sembako'),
]
