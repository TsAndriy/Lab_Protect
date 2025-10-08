# labs/urls.py
"""
URL configuration for labs app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Головна сторінка
    path('', views.index, name='index'),

    # Лабораторна робота №1 - ГПВЧ
    path('lab1/', views.lab1_prng, name='lab1'),
    path('lab1/generate/', views.generate_prng, name='generate_prng'),
    path('lab1/period/', views.test_period, name='test_period'),
    path('lab1/cesaro/', views.test_cesaro, name='test_cesaro'),
    path('lab1/randomness/', views.test_randomness, name='test_randomness'),
    path('lab1/export/', views.export_results, name='export_results'),

]