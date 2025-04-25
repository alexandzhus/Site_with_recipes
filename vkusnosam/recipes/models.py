import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager

from recipes.utils import filter_valid_lines


def translit_to_eng(s: str) -> str:
    """
    Метод для перевода русских букв в литиницу.
    :param s:
    :return: Str
    """
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))


class Recipe(models.Model):
    """
    Модель рецепта
    """
    name = models.CharField(max_length=255, verbose_name='Название блюда', db_index=True)
    slug = models.CharField(max_length=255, verbose_name="Slug", db_index=True, unique=True, blank=True)
    image = models.ImageField(blank=True, null=True, default=None,
                              upload_to='recipe_image/%Y/%m/%d', verbose_name='Изображения рецепта')
    description = models.TextField(blank=True, verbose_name='Описание рецепта')
    products = models.TextField(blank=True, verbose_name='Какие продукты')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL,
                             related_name='recipes', verbose_name='Пользователь', null=True, default=None)
    tags = TaggableManager()
    tags_category = models.ForeignKey('TagsCategory', on_delete=models.CASCADE, related_name='recipes_cat',
                                      verbose_name='Категория тегов', null=True)
    views = models.PositiveIntegerField(default=0, verbose_name='Кол-во просмотров')  # Поле для хранения количества просмотров
    number_servings = models.PositiveIntegerField(blank=True, null=True, verbose_name="Кол-во порций")
    time_preparing = models.PositiveIntegerField(blank=True, verbose_name="Время приготовления", null=True)
    calorie = models.PositiveIntegerField(blank=True, verbose_name="Калорийность", null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    def __str__(self) -> str:
        """
        Метод возвращает атрибут name в виде строки
        :return: Str
        """
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  # Если slug не указан
            self.slug = slugify(translit_to_eng(self.name))  # Генерация slug на основе имени
            while Recipe.objects.filter(slug=self.slug).exists():  # Проверка уникальности
                self.slug = f'{self.slug}-{uuid.uuid4().hex[:4]}'  # Добавление уникального суффикса
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Формирование запроса url для каждого отдельного рецепта
        :return:
        """
        return reverse("recipe_detail", kwargs={"recipe_slug": self.slug})

    def average_rating(self):
        """
        Метод для отображения среднего рейтинга рецепта.
        :return:
        """
        return self.ratings.aggregate(models.Avg('score'))['score__avg'] or 0

    def comments_quantity(self):
        """
        Метод для отображения кол-ва коменатриев.
        :return:
        """
        return self.comments.Count('comments')

    def increment_views(self):
        """
        Метод увеличивает кол-во числа просмотров.
        :return:
        """
        Recipe.objects.filter(pk=self.pk).update(views=F('views') + 1)
        self.refresh_from_db()  # Обновляем объект из базы данных

    def create_list_from_data_field_products(self) -> list:
        """
        Метод для создания списка из данных поля products.
        :return: List
        """
        # фильтруем строки, оставляя только те, которые содержат тире и заканчиваются на точку с запятой(метод из
        # файла utils.py).
        data_string = filter_valid_lines(self.products)
        # пустой словарь
        result_dict = {}
        # Обрабатываем каждую строку
        for line in data_string:
            # Проверяем, что строка заканчивается на точку с запятой
            if not line.endswith(';'):
                continue  # Пропускаем строки, которые не заканчиваются на ;
            line = line.rstrip(';').strip()
            # Разделяем строку по дефису
            key, value = line.split("-", 1)  # 1 означает, что разделяем только по первому дефису
            # Убираем лишние пробелы и добавляем в словарь
            result_dict[key.strip()] = value.strip()
        # создаем список с ключами словаря.
        keys_list = list(result_dict.keys())
        return keys_list


    class Meta:
        """
        Класс Meta отвечает за поведение полей модели
        """
        verbose_name = 'Рецепт'
        verbose_name_plural = "Рецепты"
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]


class TagsCategory(models.Model):
    """
    Модель тегов
    """
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория тега")
    slug = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="Слаг")

    def __str__(self) -> str:
        """
        Метод возвращает атрибут tag_category в виде строки
        :return: Str
        """
        return self.name

    def get_absolute_url(self) -> str:
        """
        Метод для формирования url запросов для каждого отдельного тега
        :return: Str
        """
        return reverse('tag_cloud_by_category', kwargs={"tag_category_slug": self.slug})

    class Meta:
        """
        Класс Meta отвечает за поведение полей модели
        (как будет происходить сортировка, индексация, название модели в таблице базы данных и т.д.)
        """
        verbose_name = "Категории тега"
        verbose_name_plural = 'Категория тегов'



class Comment(models.Model):
    """
    Модель для комментариев пользователей к рецепту.
    """
    content = models.TextField(verbose_name='Комментарий')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', related_name='comments')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    time_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        """
        Метод для отображения объекта модели в строковом виде.
        Отображает к какому рецепту какой пользователь оставил комментарий.
        :return: Str
        """
        return f'Комментарий пользователя {self.user} к рецепту {self.recipe}'


class Rating(models.Model):
    """
    Модель рейтинга для рецептов
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Рецепт', related_name='ratings')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='Пользователь')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Счет')

    def __str__(self) -> str:
        """
        Метод для сохранения объекта модели в строковом виде.
        Показывает какой пользователь, какому рецепту, какую оценку поставил.
        :return: Str
        """
        return f'Пользователь {self.user} поставил оценку {self.score} рецепту {self.recipe}'

    class Meta:
        """
        Клас отображающий метаданные модели.
        """
        unique_together = ('user', 'recipe') # Это команда не позволит пользователю повторно оставить оценку.
        verbose_name = 'Рейтинг'
        verbose_name_plural = "Рейтинги"


class RecipeStepPreparing(models.Model):
    """
    Модель для шагов приготовления рецепта.
    """
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name='Изображения пошагового рецепта',
                               related_name='recipes_photo')
    step_image = models.ImageField(blank=True, null=True, default=None,
                                   verbose_name='Изображения пошагового приготовления',
                                   upload_to=f'recipe_step_preparing/{recipe.name}/%Y/%m/%d')
    users = models.ForeignKey(get_user_model(), verbose_name='Пользователь', on_delete=models.CASCADE)
    # step = models.PositiveIntegerField(default=1, verbose_name='Шаг')
    step_description = models.TextField(verbose_name="Описание шага приготовления", blank=True, null=True)

    # def increment_step(self):
    #     """
    #     Метод для увеличения шага на единицу
    #     :return:
    #     """
    #     self.step += 1
    #     self.save()


    def __str__(self) -> str:
        """
        Метод для строкового отображения модели
        :return: Str
        """
        return (f'Пользователь {self.users} добавил к рецепту {self.recipe} изображение и '
                f'описание')

    class Meta:
        verbose_name = "Шаг приготовления рецепта"
        verbose_name_plural = "Шаги приготовления рецепта"
