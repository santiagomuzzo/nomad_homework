from buda import views

from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('buda/', views.TradeObtainer.as_view(), name='buda'),
]
