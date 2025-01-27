from django.urls import path

from .views import test_index_page

urlpatterns = [
    path('', test_index_page, name='index'),
]
