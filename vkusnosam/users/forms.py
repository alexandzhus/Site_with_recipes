from django import forms
from django.contrib.auth import get_user_model

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class UserLoginForm(AuthenticationForm):
    """
    Класс для отображения полей формы login.
    Используется для аутентификации пользователя.
    """
    username = forms.CharField(max_length=150, label="Логин")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']



class UserRegisterForm(UserCreationForm):
    """
    Модель для регистрации нового пользователя
    """
    username = forms.CharField(max_length=150, label="Логин")
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password1', 'password2']
        labels = {
            'email': "E-mail",
            'first_name': "Имя",
            'last_name': "Фамилия"
        }

    def clean_email(self) -> dict:
        """
        Метод проверяет базу существует-ли похожая почта
        :return: dict
        """
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует")
        return email


class Profile(forms.ModelForm):
    """
    Модель для профайла пользователя.
    """
    username = forms.CharField(disabled=True, label="Логин")
    email = forms.CharField(disabled=True, label="E-mail")

    class Meta:
        model = get_user_model()
        fields = ['username', 'avatar', 'age', 'interests', 'email', 'first_name', 'last_name',]
        labels = {
            'avatar': "Аватарка",
            'first_name': "Имя",
            'last_name': "Фамилия",
            'age': "Возраст",
            'interests': "Интересы"
        }


class UserPasswordChangeForm(PasswordChangeForm):
    """
    Форма для сброса старого пароля и создание нового
    """
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={"class": 'form-input'}))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={"class": 'form-input'}))
    new_password2 = forms.CharField(label="Подтверждение нового пароля",
                                    widget=forms.PasswordInput(attrs={"class": 'form-input'}))