"""
URL configuration for phibook project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from core.views import api_root_view
from payment.views import initiate_payment, payment_success, payment_fail, payment_cancel
from core.views import payment_success_redirect, payment_fail_redirect, payment_cancel_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
	path("", api_root_view),
	path('api/v1/', include('core.urls')),	
]

urlpatterns += [
    path('payment/initiate/', initiate_payment),   # optional: you may keep initiate routed via /api/v1 too
    path('payment/success/', payment_success_redirect),
    path('payment/fail/',    payment_fail_redirect),
    path('payment/cancel/',  payment_cancel_redirect),
]