from django import template

from recipes.models import Rating

register = template.Library()

@register.simple_tag
def user_has_rated(user, recipe):
    """
    Проверяет, поставил ли пользователь оценку для рецепта.
    """
    return Rating.objects.filter(user=user, recipe=recipe).exists()




