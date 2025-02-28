import re

from django import template
from django.db.models import Avg, Value, QuerySet
from django.db.models.functions import Coalesce

from recipes.models import Rating, Recipe

register = template.Library()

@register.simple_tag
def user_has_rated(user, recipe):
    """
    Проверяет, поставил ли пользователь оценку для рецепта.
    """
    return Rating.objects.filter(user=user, recipe=recipe).exists()


@register.simple_tag
def rating_recipes_list() -> QuerySet :
    """
    Метод для создания списка популярных рецептов.
    Возвращает первые четыре позиции.
    :return: QuerySet
    """
    queryset = Recipe.objects.all().annotate(average_rating=Coalesce(Avg('ratings__score'), Value(0.0)))
    rating_list = queryset.filter(average_rating__gte=4)[:4]
    return rating_list


@register.simple_tag
def viewing_quantity_recipes() -> QuerySet :
    """
    Метод для создания списка рецептов с наибольшим количеством просмотров.
    Возвращает первые четыре позиции.
    :return: QuerySet
    """
    queryset = Recipe.objects.all().order_by('-views')[:4]
    return queryset


@register.filter
def remove_brackets(text) -> str:
    """
    Удаляет текст в скобках из строки.
    :return: Str
    """
    return re.sub(r'\([^)]*\)', '', text).strip()