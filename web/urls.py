from web import views
from django.urls import path


urlpatterns = [
	path('', views.signin, name='signin'),
	path('dashboard', views.dashboard, name='dashboard'),
]
