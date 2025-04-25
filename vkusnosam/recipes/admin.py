from django.contrib import admin
from django.utils.safestring import mark_safe
from taggit.models import Tag

from .models import *

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Класс для отображения модели Comment в Админке.
    """
    fields = ['content', 'recipe', 'user']
    list_display = ['content', 'recipe', 'user']
    list_display_links = ['content', 'recipe', 'user']
    list_per_page = 7
    save_on_top = True
    actions_on_top = ["delete_selected"]

@admin.register(TagsCategory)
class TagsCategoryAdmin(admin.ModelAdmin):
    """
    Класс для отображения категории тегов в админке
    """
    fields = ['name', 'slug']
    list_display = ['name', 'slug']
    list_display_links = ['name', 'slug']
    prepopulated_fields = {'slug': ("name",)}
    list_per_page = 6
    save_on_top = True


# class RecipePhotosTabularInline(admin.TabularInline):
#     """
#     Класс для связанного отображения в модели Recipe и RecipePhotos
#     """
#     model = RecipePhotos
#     raw_id_fields = ['recipe']

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Клас для отображения модели Recipe в админке
    """
    fields = ['name', 'slug', 'views', 'image', 'description', 'products',
              'user', 'tags_category', 'number_servings', 'time_preparing',
              'calorie']
    list_display = ['id', 'name', 'views', 'slug', 'product_image', 'brief_description',
              'user', 'tag_list', 'number_servings', 'time_preparing',
              'calorie']
    list_display_links = ['name', 'slug']
    prepopulated_fields = {'slug': ("name",)}
    list_per_page = 6
    save_on_top = True


    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    @admin.display(description='Теги')
    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    @admin.display(description="Изображение")
    def product_image(self, recipe: Recipe):
        """
        Метод позволяет отображать поле с изображением в админке
        """
        if recipe.image:
            return mark_safe(f'<img src="{recipe.image.url}" width=50>')
        else:
            return "без изображения"

    @admin.display(description="Краткое описание рецепта")
    def brief_description(self, recipe: Recipe):
        """
        Выводит сокращенное описание рецепта.
        :param recipe:
        :return:
        """
        return f'{recipe.description[0:75]}' + "..."


# admin.site.register(RecipePhotos)
admin.site.register(Rating)
admin.site.register(RecipeStepPreparing)