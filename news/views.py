import logging
from time import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string

from django.urls import reverse_lazy, resolve
from django.utils import timezone
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView

from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
# from django.views.decorators.cache import cache_page

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
logger = logging.getLogger("django")


# @cache_page(60 * 15)  # D7.3. Кэширование в Django (view)
class PostsList(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    ordering = ['-dateCreation']
    form_class = PostForm
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        context['posts_count'] = Post.objects.all().count()  # добавим переменную кол-во постов
        context['form'] = PostForm()
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)  # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid():  # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
            form.save()
        return super().get(request, *args, **kwargs)


class PostSearch(ListView):
    model = Post
    template_name = 'news/postSearch.html'
    context_object_name = 'posts'
    ordering = ['-id']
    form_class = PostForm
    paginate_by = 5

    def get_queryset(self):
        queryset = PostFilter(self.request.GET, super().get_queryset()).qs
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        context['posts_count'] = Post.objects.all().count()  # добавим переменную кол-во постов всего
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class PostDetailView(DetailView):
    template_name = 'news/post_detail.html'
    queryset = Post.objects.all()

    # D7.4 Кэширование на низком уровне (смотри еще модель Post метод save)
    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно
        obj = cache.get(f'product-{self.kwargs["pk"]}', None)  # кэш очень похож на словарь, и
        # метод get действует также. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'product-{self.kwargs["pk"]}', obj)
        return obj


# class PostCreateView(LoginRequiredMixin, CreateView):
class PostCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'news/post_create.html'
    form_class = PostForm
    permission_required = ('news.add_post',)


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'news/post_update.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    def get_object(self, **kwargs):
        id_pk = self.kwargs.get('pk')
        return Post.objects.get(pk=id_pk)


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = reverse_lazy('news:posts')
    permission_required = ('news.delete_post',)


class CategoriesListView(ListView):
    model = Category
    template_name = 'news/categories.html'
    context_object_name = 'categories'
    ordering = ['-name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class CategoryDetailView(ListView):
    model = Category
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    ordering = ['-id']
    # ordering = ['-dateCreation']
    paginate_by = 5

    def get_queryset(self):
        cat = Category.objects.get(pk=self.kwargs['pk'])
        queryset = cat.post_set.order_by('-pk')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(pk=self.kwargs['pk'])
        context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required()
def subscribe_to(request, pk):
    user = request.user
    category = Category.objects.get(pk=pk)
    logger.info(f"== Пользователь: '{user}' подписался на категорию: '{category}' ==")

    if not category.subscribers.filter(pk=user.id).exists():
        category.subscribers.add(user)
        email = user.email
        html = render_to_string(
            'mail/subscribe.html',
            {
                'category': category,
                'user': user
            },
        )
        msg = EmailMultiAlternatives(
            subject=f'Вы подписались на категорию {category}',
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[email, ],
        )

        msg.attach_alternative(html, 'text/html')

        try:
            msg.send()
        except Exception as e:
            print(e)
        # return redirect(request.META.get('HTTP_REFERER'))
        return redirect('news:categories')

    return redirect(request.META.get('HTTP_REFERER'))
    # return redirect('news:categories')


@login_required()
def unsubscribe_from(request, pk):
    user = request.user
    category = Category.objects.get(pk=pk)
    logger.info(f"== Пользователь: '{user}' отписался от категории: '{category}' ==")
    if category.subscribers.filter(id=user.id).exists():
        category.subscribers.remove(user)
    return redirect('news:categories')
    # return redirect(request.META.get('HTTP_REFERER'))


# --------------------------------
# def div_zero():
#     result = 5 / 0
#     logger.error("Деление на ноль!!!")

# -------------------------------
# class Category2DetailView(ListView):
#     model = Post
#     template_name = 'news/posts.html'
#     context_object_name = 'posts'
#     ordering = ['-id']
#     paginate_by = 3
#
#     def get_queryset(self):
#         self.id = resolve(self.request.path_info).kwargs['pk']
#         print("==1 =====", self.id)
#         print("== 1.1 =====", self.kwargs['pk'])
#
#         cat = Category.objects.get(pk=self.kwargs['pk'])
#         queryset = cat.post_set.order_by('-pk')
#         return queryset
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         print("==2 =====", self.id)
#         print("== 2.2 =====", self.kwargs['pk'])
#         context['category'] = Category.objects.get(pk=self.kwargs['pk'])
#         context['time_now'] = timezone.localtime(timezone.now())  # добавим переменную текущей даты time_now
#         context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
#         return context
# -------------------------------
