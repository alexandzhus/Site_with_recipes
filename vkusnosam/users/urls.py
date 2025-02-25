from django.contrib.auth.views import LogoutView
from django.contrib.gis.gdal.prototypes.srs import from_user_input
from django.urls import path, reverse_lazy

from .views import CustomLoginView, RegisterView, ProfileView

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Сброс пароля

]
