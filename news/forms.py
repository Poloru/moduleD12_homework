from django.forms import ModelForm
from .models import Post, Category
from django import forms


# Создаём модельную форму
class PostForm(ModelForm):
    # В класс мета, как обычно, надо написать модель,
    # по которой будет строиться форма, и нужные нам поля.
    # Мы уже делали что-то похожее с фильтрами
    class Meta:
        model = Post
        fields = ['author', 'categoryType', 'postCategory',
                  'title', 'text']

        widgets = {
            'author': forms.Select(attrs={'class': 'form-control'}),
            'categoryType': forms.Select(attrs={'class': 'form-control',}),
            'postCategory': forms.SelectMultiple(attrs={'class': 'form-control',}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название статьи или новости'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Сама статья'
            }),
        }

