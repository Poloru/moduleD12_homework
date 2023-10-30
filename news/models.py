from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Sum


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete=models.CASCADE)
    ratingAuthor = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.authorUser.username

    def update_rating(self):
        postRat = self.post_set.all().aggregate(postRating=Sum('rating'))
        pRat = 0
        pRat += postRat.get('postRating')

        commentRat = self.authorUser.comment_set.all().aggregate(commentRating=Sum('rating'))
        cRat = 0
        cRat += commentRat.get('commentRating')

        # ------суммарный рейтинг всех комментариев к статьям автора.---------
        posts = self.post_set.all()
        commentPostRat = 0
        for post in posts:
            commentPostRow = post.comment_set.all().aggregate(cpRating=Sum('rating'))
            commentPostRat += commentPostRow.get('cpRating')
        self.ratingAuthor = pRat * 3 + cRat + commentPostRat
        # -------------------------------
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/news/categories/{self.pk}'


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')

    NEWS = 'NW'
    ARTICLE = 'AR'

    TYPES = [
        (NEWS, 'Новость'),
        (ARTICLE, 'Статья'),
    ]

    categoryType = models.CharField(max_length=2, choices=TYPES, default=ARTICLE, verbose_name='Тип статьи')
    dateCreation = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    postCategory = models.ManyToManyField(Category, through='PostCategory', verbose_name='Категории статьи')
    title = models.CharField(max_length=128, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст статьи')
    rating = models.SmallIntegerField(default=0, verbose_name='Рейтинг')

    @property
    def in_categories(self):
        list_categories = []
        for c in self.postCategory.all():
            list_categories.append(c.name)
        return list_categories

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.pk}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:123] + '...'

    # D7.4.Кэширование на низком уровне (смотри еще view PostDetailView метод get_object)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'product-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    postThrough = models.ForeignKey(Post, on_delete=models.CASCADE)
    categoryThrough = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.categoryThrough}: {self.postThrough}'


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete=models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dateCreation = models.DateTimeField(auto_now_add=True)
    rating = models.SmallIntegerField(default=0)

    def __str__(self):
        return f'{self.commentUser.username}: {self.commentPost.title}: {self.text[0:15] + "..."}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


