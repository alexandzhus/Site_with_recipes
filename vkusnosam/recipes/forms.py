from django import forms
from django.core.exceptions import ValidationError
from django.db.transaction import commit

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
            'image': 'Изображение ',
            'tags_category': 'Выберите к какому типа блюда относится рецепт ',
            'time_preparing': 'Время приготовления (мин.)   ',
            'calorie': 'Калорийность (на одну порцию)   ',
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
        elif len(name) > 255:
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

    def save(self, commit=True) -> Recipe:
        """
        Метод берет названия продуктов из поля products, после чего создает их них список.
        Далее из списка создаются привязанные к рецепту теги.
        :param commit: Если True, сохраняет объект в БД. Если False, возвращает несохраненный объект.
        :return: Объект модели Recipe (сохраненный или нет, в зависимости от commit)
        """
        recipe = super().save(commit=False)  # Получаем несохраненный объект Recipe

        if commit:
            recipe.save()  # Сохраняем рецепт в БД
            self.save_m2m()  # Сохраняем ManyToMany-поля (если есть)

            # Обрабатываем продукты и добавляем теги
            products_text = self.cleaned_data.get('products', '')
            print(products_text)
            if products_text:
                product_names = recipe.create_list_from_data_field_products()  # Получаем список названий
                print(product_names)
                recipe.tags.add(*product_names)

        return recipe




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
        widgets = {'content': forms.Textarea(attrs={
            'rows': 3,
            'cols': 25,
        }),
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
        elif len(content) > 3000:
            raise ValidationError("Длина более 3000 символов. Слишком длинный комментарий!")
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

