from web import views
from django.urls import path, re_path

urlpatterns = [
    path('', views.signin, name='signin'),
    path('logout', views.logoutUser, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('room', views.room, name='room'),
    path('income', views.income, name='income'),
    path('worker', views.worker, name='worker'),
    path('product/', views.product, name='product'),
    path('worker/add', views.user_new, name='user_new'),
    path('worker/<int:pk>/', views.user_edit, name='user_edit'),
    path('worker/<int:pk>/delete', views.user_delete, name='user_delete'),
    path('category/<int:pk>/', views.category_edit, name='category'),
    path('category/new/', views.category_new, name="category_new"),
    path('category/<int:pk>/delete', views.category_delete, name="category_delete"),
    path('product/food/<int:pk>/', views.food_edit, name='food_edit'),
    path('product/food/new/', views.food_new, name="food_new"),
    path('product/<int:pk>/delete', views.food_delete, name="food_delete"),
    path('rooms', views.rooms, name='rooms'),
    path('rooms/new', views.room_new, name='room_new'),
    path('rooms/<int:pk>/tables', views.room_tables, name='room_tables'),
    path('rooms/<int:pk>/', views.room_edit, name='room_edit'),
    path('rooms/<int:pk>/delete', views.room_delete, name='room_delete'),
    path('order', views.order, name='order'),
    path('document', views.document, name='document'),
]
