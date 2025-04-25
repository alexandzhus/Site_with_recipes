from django import forms
from django.core.exceptions import ValidationError

from recipes.models import Recipe, Comment, Rating, RecipeStepPreparing


def validate_text_format(value):
    """
    Пользовательский валидатор.
    Проверяет, что данные внесены правильно:
    в поле были введены данные через пробел и заканчиваются точкой с запятой.
    :param value:
    :return:
    """
    lines = value.strip().split('; ') # Разделяем данные по точке с запятой
    for line in lines:
        if line.strip():  # Пропускаем пустые строки
            if '-' not in line:
                raise ValidationError(
                    f'Ошибка в строке: "{line}". Между продуктом и граммовками надо ставить дефис(Мука - 150гр.;)'
                )
            if ';' not in line:
                raise ValidationError(
                    f'Ошибка в строке: "{line}". Каждая строка должна заканчиваться точкой с запятой ;'
                )


class RecipeForm(forms.ModelForm):
    """
    Форма для модели рецепта
    """
    class Meta:
        model = Recipe
        fields = ['name', 'image', 'description', 'products', 'number_servings',
                  'time_preparing', 'tags_category', 'calorie']
        labels = {
            'tags_category': 'Выберите к какому типа блюда относится рецепт',
            'time_preparing': 'Время приготовления (мин. )',
            'calorie': 'Калорийность (на одну порцию )',
        }
        validators = {
            'products': [validate_text_format],
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
    def clean_products(self) -> str:
        """
        Метод для проверки валидности поля products.
        Проверят, что в поле было заполнено правильно.
        :return: Str
        """
        products = self.cleaned_data['products']
        validate_text_format(products)
        return products


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
    sort_by = forms.ChoiceField(
        label='Сортировать по: ', choices=[
            ('', '--Выбрать--'),
            ('-time_create', '---Новые рецепты первые---'),
            ('time_create', '---Старые рецепты первые---'),
            ('-comments_quantity', '---Кол-ву комментариев(Больше всего комментариев)---'),
            ('comments_quantity', '---Кол-ву комментариев(Меньше всего комментариев)---'),

        ], required=False
    )


class RatingSortForm(forms.Form):
    sort_by_ratings = forms.ChoiceField(
        label='По рейтингу: ', choices=[
            ('', '--Выбрать--'),
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


class RecipeStepPreparingForm(forms.ModelForm):
    """
    Форма для добавления шагов приготовления рецепта
    """

    class Meta:
        model = RecipeStepPreparing
        fields = ['step_image', 'step_description']
        widgets = {
        'step_description' : forms.Textarea(attrs={'cols': 30, 'rows': 5}),
        }

