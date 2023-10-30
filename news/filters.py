import django_filters
from django import forms
from django_filters import FilterSet, ModelChoiceFilter  # импортируем filterset, чем-то напоминающий знакомые дженерики
from .models import Post, Author, Category


class PostFilter(django_filters.FilterSet):
    dateCreation = django_filters.DateFilter(
        field_name='dateCreation',
        label='Дата создания позже чем',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'DD-MM-YYYY'}),
        input_formats=['%d-%m-%Y', '%d-%m', '%m', '%d', '%m-%Y', '%Y-%m-%d', '%Y-%m', '%m-%d', '%d.%m.%Y']
    )
    author = ModelChoiceFilter(field_name='author', label='Автор', lookup_expr='exact',
                               queryset=Author.objects.all())

    postCategory = ModelChoiceFilter(field_name='postCategory', label='Категория', lookup_expr='exact',
                                     queryset=Category.objects.all())

    class Meta:
        model = Post
        fields = ['dateCreation', 'author', 'postCategory']

        # fields = {
        #     'dateCreation': ['gte'],
        #     'author': ['exact'],
        #           }


