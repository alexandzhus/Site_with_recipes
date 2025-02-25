from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, Comment, Rating


class RecipeForm(forms.ModelForm):
    """
    Форма для модели рецепта
    """
    class Meta:
        model = Recipe
        fields = ['name', 'image', 'description', 'products', 'number_servings',
                  'time_preparing', 'tags_category','calorie', 'steps_description']
        labels = {
            'tags_category': 'Выберите к какому типа блюда относится рецепт',
        }

    def clean_name(self) -> str:
        """
        Метод для проверки поля формы name.
        Проверяет на минимальное и максимальное количество символов.
        :return: Str
        """
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise ValidationError("Длина менее 3 символов")
        elif len(name) > 50:
            raise ValidationError("Длина более 50 символов")
        return name


class CommentForm(forms.ModelForm):
    """
    Форма для модели Comment
    """
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': "Комментарий"
        }

    def clean_content(self) -> str:
        """
        Метод для проверки поля формы content.
        Проверяет на минимальное(2) и максимальное(1000) количество символов.
        :return: Str
        """
        content = self.cleaned_data['content']
        if len(content) < 2:
            raise ValidationError("Длина менее 2 символов. Слишком короткий комментарий!")
        elif len(content) > 1000:
            raise ValidationError("Длина более 1000 символов. Слишком длинный комментарий!")
        return content


class SearchSortForm(forms.Form):
    """
    Форма для поиска.
    """
    search = forms.CharField(label='Поиск', max_length=255, required=False)
    sort_by = forms.ChoiceField(
        label='Сортировать по: ', choices=[
            ('', 'Выбрать'),
            ('-time_create', '---Новые рецепты первые---'),
            ('time_create', '---Старые рецепты первые---'),
            ('-comments_quantity', '---Кол-ву комментариев(Больше всего комментариев)---'),
            ('comments_quantity', '---Кол-ву комментариев(Меньше всего комментариев)---'),

        ], required=False
    )


class RatingSortForm(forms.Form):
    sort_by_ratings = forms.ChoiceField(
        label='По рейтингу: ', choices=[
            ('', 'Выбрать'),
            ('-ratings', '---По рейтингу(больше)---'),
            ('ratings', '---По рейтингу(меньше)---'),
        ], required=False
    )


class RatingForm(forms.ModelForm):
    """
    Форма для отображения рейтинга
    """
    class Meta:
        model = Rating
        fields = ['score']
        labels = {
            'score': 'Оценка'
        }