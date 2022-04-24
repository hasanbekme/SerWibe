from web import views
from django.urls import path

urlpatterns = [
    path('', views.signin, name='signin'),
    path('logout', views.logoutUser, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('room', views.room, name='room'),
    path('income', views.income, name='income'),
    path('worker', views.worker, name='worker'),
    path('product', views.product, name='product'),
    path('category/<int:ids>/', views.category, name='category'),
    path('table', views.table, name='table'),
    path('order', views.order, name='order'),
    path('document', views.document, name='document'),
]
