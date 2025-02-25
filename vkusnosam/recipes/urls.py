from django.urls import path

from .views import HomeView, RecipeDetail, CreateRecipe, UpdateRecipe, DeleteRecipe, TagCloudByCategoryView, \
    TaggedRecipesView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('recipe_detail/<slug:recipe_slug>/', RecipeDetail.as_view(), name='recipe_detail'),

    path('tag-cloud/', TagCloudByCategoryView.as_view(), name='tag_cloud_by_category'),
    path('tag-cloud/<slug:tag_category_slug>/', TagCloudByCategoryView.as_view(), name='tag_cloud_by_category'),
    path('tag/<str:tag_slug>/', TaggedRecipesView.as_view(), name='tagged_recipes'),

    path('create_recipe/', CreateRecipe.as_view(), name='create_recipe'),
    path('update_recipe/<slug:slug>/', UpdateRecipe.as_view(), name='update_recipe'),
    path('delete_recipe/<slug:slug>/', DeleteRecipe.as_view(), name='delete_recipe'),
]
