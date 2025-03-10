from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('module-instances/', views.list_module_instances, name='module_instances'),
    path('professors/', views.list_professors, name='professors'),
    path('ratings/average/', views.average_rating, name='average_rating'),
    path('rate/', views.rate_professor, name='rate_professor'),
]
