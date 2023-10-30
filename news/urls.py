from django.urls import path
from django.views.decorators.cache import cache_page

from .views import PostsList, PostDetailView, PostSearch, PostCreateView, \
    PostUpdateView, PostDeleteView, CategoriesListView, CategoryDetailView, subscribe_to, unsubscribe_from

app_name = 'news'
urlpatterns = [
    # path('', cache_page(10*1)(PostsList.as_view()), name='posts'),  # D7.3. Кэширование в Django (view, url)
    path('', PostsList.as_view(), name='posts'),
    path('search/', PostSearch.as_view()),

    # path('<int:pk>', cache_page(10*5)(PostDetailView.as_view()), name='post_detail'),
    path('<int:pk>', PostDetailView.as_view(), name='post_detail'),
    path('add/', PostCreateView.as_view(), name='post_create'),

    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

    path('categories/', CategoriesListView.as_view(), name='categories'),
    path('categories/<int:pk>', CategoryDetailView.as_view(), name='category_detail'),

    path('subscribe/<int:pk>', subscribe_to, name='subscribe'),
    path('unsubscribe/<int:pk>', unsubscribe_from, name='unsubscribe'),

]

