from http.client import responses
from typing import Dict

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _


from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import UserLoginForm, UserRegisterForm, Profile, UserPasswordChangeForm

from recipes.models import Recipe, Comment


class CustomLoginView(LoginView):
    """
    Представление для авторизации пользователя
    """
    authentication_form = UserLoginForm
    template_name = 'users/login_form.html'
    extra_context = {'title': 'Авторизация'}
    success_url = 'home'


    def get_success_url(self) -> str:
        """
        Метод для переадресации суперпользователя в админ панель
        :return: str (URL для перенаправления)
        """
        if self.request.user.is_superuser:
            return reverse_lazy('admin:index') # возвращает '/admin'
        return super().get_success_url() # возвращает '/home'


    def form_valid(self, form: any) -> str:
        """
        Выводит сообщение об успешной авторизации если данные формы валидны
        :param form: form
        :return: str
        """
        response = super().form_valid(form)
        messages.success(self.request, _("Добро пожаловать! Вы успешно авторизовались в системе!"))
        return response

    def form_invalid(self, form: any) -> str:
        """
        Выводит сообщение об ошибке авторизации если данные формы не валидны
        :param form: form
        :return: str
        """
        response = super().form_invalid(form)
        messages.error(self.request, _("Ошибка! Неверно введен логин или пароль! Попробуйте еще раз!"))
        return super().form_invalid(form)



class RegisterView(CreateView):
    """
    Представление для создания нового пользователя
    """
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    extra_context = {
        'title': "Регистрация нового пользователя",
    }


class ProfileView(UpdateView):
    """
    Представление для отображения и обновления профиля пользователя.
    """
    model = get_user_model()
    form_class = Profile
    success_url = reverse_lazy('users:profile')
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        """
        Метод для получения текущего юзера из базы.
        Возвращает текущего аутентифицированного пользователя.
        :param queryset: None
        :return:
        """
        return self.request.user

    def get_context_data(self, **kwargs) -> Dict:
        """
        Метод для получения связанных данных. Получает все рецепты опубликованные пользователем.
        :param kwargs:
        :return: Dict
        """
        context = super().get_context_data(**kwargs)
        users_recipes = Recipe.objects.filter(user=self.request.user)
        users_comments = Comment.objects.filter(user=self.request.user)
        context['users_recipes'] = users_recipes
        context['users_comments'] = users_comments
        return context

    def form_valid(self, form: any) -> str:
        """
        Выводит сообщение об успешном обновлении профиля пользователя если форма валидна.
        :param form: form
        :return: str
        """
        response = super().form_valid(form)
        messages.success(self.request, _("Вы успешно обновили свой профиль!"))
        return response

    def form_invalid(self, form: any) -> str:
        """
        Выводит сообщение об ошибке если форма не валидна.
        :param form: Any
        :return: str
        """
        response = super().form_invalid(form)
        messages.error(self.request, _("Ошибка! Попробуйте еще раз!"))
        return super().form_invalid(form)


class UserPasswordChangeView(PasswordChangeView):
    """
    Представление для смены старого пароля на новый
    """
    form_class = UserPasswordChangeForm
    template_name = 'users/password/password-change-form.html'
    success_url = reverse_lazy('users:password-change-done')
    extra_context = {
        'title': "Смена пароля"
    }

