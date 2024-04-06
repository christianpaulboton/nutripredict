from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('', views.landing_page, name='landing_page'),          
    path('about', views.about_view, name='about'),
    path('output', views.output_view, name='output'),
    path('home', views.home_view, name='home'),
    path('our_team', views.our_team_view, name='our_team'),
    path('home', views.home_view, name='home_view'),
    path('contact_us/', views.contact_us_view, name='contact_us'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('predict/', views.predict_view, name='predict_view'), 
    path('login/', views.log_in_view, name='login'),
    path('signup/', views.sign_up, name='signup'),
    path('overtime/', views.overtime_view, name='overtime'),
    path('delete/<int:prediction_id>/', views.delete_prediction, name='delete_prediction'),
    path('logout/', views.logout_view, name='logout'),
    path('reset/', views.reset_view, name='reset'),
    path('password/', views.change_password_view, name='change_password'),
    path('graph/', views.nutritional_graph_view, name='nutritional_graph'),
    path('sex/', views.sex_graph_view, name='sex_graph'),
    path('age/', views.age_graph_view, name='age_graph'),
    path('height/', views.height_graph_view, name='height_graph'),
    path('weight/', views.weight_graph_view, name='weight_graph'),
    path('bar/', views.bar_graph_view, name='bar_graph'),

]