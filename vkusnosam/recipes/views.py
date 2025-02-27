import logging
from typing import Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Avg, Value, QuerySet
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.views.generic.edit import FormMixin
from taggit.models import Tag

from .forms import RecipeForm, CommentForm, SearchSortForm, RatingForm, RatingSortForm
from .models import Recipe, RecipePhotos, Comment, Rating, TagsCategory

logger = logging.getLogger(__name__)  # Экземпляр logging, который мы можем использовать.

# class AuthorRequiredMixin:
#     """
#     Миксин для проверки, является ли пользователь автором поста.
#     """
#
#     def dispatch(self, request, *args, **kwargs):
#         recipe = Recipe.get_object()
#         if recipe.user != request.user:
#             raise PermissionDenied
#         return super().dispatch(request, *args, **kwargs)


class HomeView(ListView):
    """
    Класс для отображения списка рецептов
    """
    model = Recipe
    context_object_name = 'recipes'
    template_name = 'recipes/index.html'
    paginate_by = 4

    def get_queryset(self) -> QuerySet:
        """
        Метод для сортировки рецептов.
        Сортирует по дате, по кол-ву комментариев, по рейтингу.
        :return: QuerySet
        """
        queryset = Recipe.objects.all().annotate(comments_quantity=Count('comments'),
                                                 average_rating=Coalesce(Avg('ratings__score'), Value(0.0))
                                                 ).select_related('user').prefetch_related('comments', 'ratings')
        # for i, x in enumerate(queryset):
        #     if i == 0:
        #         print(list(x.__dict__)[1:])
        #     print(list(x.__dict__.values())[1:])
        query = self.request.GET.get('search')
        sort_by_ratings = self.request.GET.get('sort_by_ratings')
        sort_by = self.request.GET.get('sort_by', '-time_create')
        if query:
             queryset = queryset.filter(Q(name__iregex=query) | Q(products__iregex=query))
        if sort_by in['time_create', '-time_create', 'comments_quantity', '-comments_quantity']:
            queryset = queryset.order_by(sort_by)
        if sort_by_ratings == '-ratings':
            queryset = queryset.order_by('-average_rating')
        if sort_by_ratings == 'ratings':
            queryset = queryset.order_by('average_rating')

        return queryset


    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Метод для добавления контекста к представлению.
        Добавляем формы для сортировки.
        :param object_list:
        :param kwargs:
        :return:
        """
        context = super().get_context_data(**kwargs)
        context['title'] = 'Главная страница'
        context['search_form'] = SearchSortForm(self.request.GET)
        context['rating_form'] = RatingSortForm(self.request.GET)
        return context


class TagCloudByCategoryView(ListView):
    """
    Представление для отображения облака тегов.
    """
    template_name = 'recipes/tag_cloud.html'
    context_object_name = 'tags'

    def get_queryset(self) -> QuerySet:
        """
        Метод для получения категории тегов.
        :return: QuerySet
        """
        tag_category_slug = self.kwargs.get('tag_category_slug')
        if tag_category_slug:
            category_tag = get_object_or_404(TagsCategory, slug=tag_category_slug)
            tags = Tag.objects.filter(recipe__tags_category=category_tag
                                      ).annotate(num_times=Count('taggit_taggeditem_items')).order_by('name')
        else:
            tags = Tag.objects.annotate(num_times=Count('taggit_taggeditem_items')).order_by('name')

        if tags.exists(): # Рассчитываем вес для каждого тега
            max_count = max(tag.num_times for tag in tags)  # Максимальное количество использований
            for tag in tags:
                # Нормализуем вес тега (например, от 1 до 5)
                tag.weight = int((tag.num_times / max_count) * 5) if max_count > 0 else 1
        print(tags)
        return tags

    def get_context_data(self, *, object_list=None, **kwargs) -> dict:
        """
        Метод для передачи контекста в шаблон.
        Передаем категории тегов.
        :param object_list:
        :param kwargs:
        :return: Dict
        """
        context = super().get_context_data(**kwargs)
        tag_category_slug = self.kwargs.get('tag_category_slug')
        if tag_category_slug:
            context['category_tag'] = get_object_or_404(TagsCategory, slug=tag_category_slug)
        else:
            context['category_tag'] = None
        context['categorys_tags'] = TagsCategory.objects.all()
        return context



class TaggedRecipesView(ListView) :
    """
    Представление для фильтрации рецептов с конкретным тегом.
    """
    template_name = 'recipes/tagged_recipes.html'
    context_object_name = 'recipes'

    def get_queryset(self) -> QuerySet:
        """
        Метод для получения списка объектов.
        Возвращает список рецептов связанных с определенным тегом.
        :return: QuerySet
        """
        tag_slug = self.kwargs.get('tag_slug')
        self.tag = get_object_or_404(Tag, slug=tag_slug)
        return Recipe.objects.filter(tags__in=[self.tag])

    def get_context_data(self, **kwargs) -> dict:
        """
        Метод для передачи контекста в шаблон.
        Передаем контекст для объекта тег.
        :param kwargs:
        :return: Dict
        """
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context



class RecipeDetail(FormMixin, DetailView):
    """
    Представление для отображения детальной информации о рецепте.
    """
    model = Recipe
    form_class = CommentForm
    context_object_name = 'recipe'
    slug_url_kwarg = 'recipe_slug'
    template_name = 'recipes/recipe_detail.html'

    def get_success_url(self):
        """
        Метод для перенаправления после успешного добавления комментария.
        Перенаправляет обратно в рецепт.
        :return:
        """
        recipe = self.get_object()
        return recipe.get_absolute_url()
        # return reverse("recipe_detail", kwargs={"recipe_slug": self.slug})

    def get_context_data(self, **kwargs) -> dict:
        """
        Метод для получения связанных данных и передачи контекста в представление.
        Получает все картинки и комментарии, связанные с рецептом. Также форму для
        комментариев.
        :param kwargs:
        :return: Dict
        """
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()
        recipe_photos = RecipePhotos.objects.filter(recipe_id=recipe)
        comments = recipe.comments.all()
        comments_form = self.get_form()
        context['recipe_photos'] = recipe_photos
        context['title'] = f"Детальная информация о рецепте {recipe.slug}"
        context['comments'] = comments
        context['comments_form'] = comments_form
        context['rating_form'] = RatingForm()
        return context


    def get_object(self, queryset=None):
        """
        Метод для получения определенного рецепта из базы данных.
        Возвращает выбранный объект по slug
        :param queryset:
        :return:
        """
        return get_object_or_404(Recipe, slug=self.kwargs[self.slug_url_kwarg])

    def post(self, request, *args, **kwargs):
        """
        Метод ддя обработки POST-запроса (добавление комментария)
        """
        self.object = self.get_object()  # Получаем объект рецепта
        form = self.get_form()
        rating_form = RatingForm(request.POST)
        if form.is_valid():
            return self.form_valid(form)
        if rating_form.is_valid():
            return self.form_valid(rating_form)
        else:
            return self.form_invalid(form) or self.form_invalid(rating_form)


    def form_valid(self, form):
        """
        Метод для сохранения комментария.
        """
        comment = form.save(commit=False) # сохраняем, но не коммитим изменения
        comment.recipe = self.object  # Привязываем комментарий к рецепту
        comment.user = self.request.user  # Указываем автора комментария
        comment.save()
        return super().form_valid(form)




class CreateRecipe(LoginRequiredMixin, CreateView):
    """
    Представление для создания нового рецепта.
    """
    model = Recipe
    login_url = reverse_lazy('users:login')
    form_class = RecipeForm
    template_name = 'recipes/create_recipe_form.html'
    extra_context = {
        'title': 'Создание нового рецепта!'
    }

    def form_valid(self, form):
        """
        Функция проверки на валидность. После чего происходит объект записи без занесения в базу данных(commit=False),
        привязка пользователя к форме и сохранение в БД при помощи возвращения
        самой себя через метод super()
        :param form:
        :return:
        """
        recipe = form.save(commit=False)
        recipe.user = self.request.user   #   user хранить имя текущего пользователя создающего статью
        return super().form_valid(form)



class UpdateRecipe(UserPassesTestMixin, UpdateView):
    """
    Представление для обновления данных рецепта.
    """
    model = Recipe
    template_name = 'recipes/update_recipe.html'
    form_class = RecipeForm

    def test_func(self):
        """
        Метод для проверки прав пользователя. Проверяется что текущий пользователь является
        автором рецепта.
        :return:
        """
        recipe = self.get_object()
        user = self.request.user
        # Логируем информацию о пользователе и рецепте
        logger.info(f"Пользователь {user.username} пытается изменить рецепт {recipe.slug}")
        if user == recipe.user:
            logger.info(f"Доступ разрешен: пользователь {user.username} является автором рецепта {recipe.slug}")
            return True
        else:
            logger.warning(f"Доступ запрещен: пользователь {user.username} не является автором рецепта {recipe.slug}")
            return False

    def get_context_data(self, **kwargs) -> Dict:
        """
        Метод для получения контекста.
        :param kwargs:
        :return: Dict
        """
        recipe = self.get_object()
        context = super().get_context_data(**kwargs)
        context['title'] = f'Обновление рецепта {recipe.slug}'
        return context




class DeleteRecipe(UserPassesTestMixin, DeleteView):
    """
    Представление для удаления рецепта.
    """
    model = Recipe
    template_name = 'recipes/delete_recipe.html'
    success_url = reverse_lazy('home')
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs) -> Dict:
        """
        Метод для получения контекста.
        :param kwargs:
        :return: Dict
        """
        recipe: Recipe = self.object
        context = super().get_context_data(**kwargs)
        context['title'] = f'Удаление рецепта {recipe.slug}'
        return context


    def test_func(self):
        """
        Метод для проверки прав пользователя. Проверяется что текущий пользователь является
        автором рецепта
        :return:
        """
        recipe = self.get_object()
        user = self.request.user
        # Логируем информацию о пользователе и рецепте
        logger.info(f"Пользователь {user.username} пытается удалить рецепт {recipe.slug}")
        if user == recipe.user:
            logger.info(f"Доступ разрешен: пользователь {user.username} является автором рецепта {recipe.slug}")
            return True
        else:
            logger.warning(f"Доступ запрещен: пользователь {user.username} не является автором рецепта {recipe.slug}")
            return False




def page_permission_denied(request, exception):
    """
    Представления для перехода на шаблон, в случае если у пользователя нет прав и появляется ошибка 403.
    :param request:
    :param exception:
    :return:
    """
    return HttpResponseForbidden(render(request,'recipes/denied.html'))
