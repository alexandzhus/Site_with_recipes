from django.contrib.auth.views import LogoutView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView

from django.urls import path, reverse_lazy

from .views import CustomLoginView, RegisterView, ProfileView, UserPasswordChangeView

app_name = 'users'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Изменение и сброс пароля
    path('password-change/', UserPasswordChangeView.as_view(), name='password-change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(
        template_name='users/password/password-change-done.html'), name='password-change-done'),

    path('password-reset/', PasswordResetView.as_view(
        template_name='users/password/password-reset-form.html',
        email_template_name="users/password/password_reset_email.html",
        success_url = reverse_lazy('users:password_reset_done')),
        name='password_reset'),

    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='users/password/password-reset-done.html'), name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name="users/password/password_reset_confirm.html",
             success_url = reverse_lazy('users:password_reset_complete')), name='password_reset_confirm'),

    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name="users/password/password_reset_complete.html"),
         name='password_reset_complete'),

]
