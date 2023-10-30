from django.contrib import admin

from .models import Author, Category, Post, Comment, PostCategory

admin.site.register(Author)
admin.site.register(Category)
# admin.site.register(Post)
# admin.site.unregister(Post)
admin.site.register(Comment)
admin.site.register(PostCategory)


# напишем уже знакомую нам функцию обнуления товара на складе
def nullfy_quantity(modeladmin, request, queryset):  # все аргументы уже должны быть вам знакомы,
    # самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо
    # говоря набор объектов, которых мы выделили галочками.
    queryset.update(quantity=0)
    nullfy_quantity.short_description = 'Обнулить товары' # описание для более понятного
    # представления в админ панеле задаётся, как будто это объект


# создаём новый класс для представления товаров в админке
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'in_categories', 'author', 'categoryType', 'dateCreation', 'text')  # оставляем только имя и цену товара
    list_filter = ('author', 'categoryType', 'postCategory__name', 'dateCreation')
    # search_fields = ('title', 'author', 'postCategory__name')
    search_fields = ('title', 'text')
    # list_filter = ('title', 'in_categories', 'author', 'categoryType', 'dateCreation')
    actions = [nullfy_quantity]  # добавляем действия в список


admin.site.register(Post, PostAdmin)


# Register your models here.
# list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
# list_display = [field.name for field in Post._meta.get_fields()]  # генерируем список имён всех полей для более красивого отображения
# list_display = ('title', 'author', 'categoryType', 'dateCreation', 'text', 'postCategory')  # оставляем только имя и цену товара


