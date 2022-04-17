from web import views
from django.urls import path


urlpatterns = [
	path('', views.signin, name='signin'),
	path('dashboard', views.dashboard, name='dashboard'),
	path('income', views.income, name='income'),
	path('worker', views.worker, name='worker'),
	path('product', views.product, name='product'),
]
