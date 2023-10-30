from django import template

register = template.Library()

banned_word_list = [
    'Редиска',
    'канай',
    'дурак',
    'дура',
    'Петух',
    'Моргалы'
]


@register.filter(name='Censor')
def censor(text):
    for bw in banned_word_list:
        text = text.lower().replace(bw.lower(), f'{bw[0:2]}...')
    return text


# -------------  Задание 12.2.6 -----------------
# Реализуйте фильтр, который заменяет все буквы кроме первой и последней на «*» у слов
# из списка «нежелательных». Предполагается, что в качестве аргумента гарантированно
# передается текст, и слова разделены пробелами. Можно считать, что запрещенные слова
# находятся в списке forbidden_words.

# ---- Ответ ----------

@register.filter(name='Censor2')
def hide_forbidden(text):
    words = text.split()
    result = []
    for word in words:
        # if word in forbidden_words:
        if word in banned_word_list:
            result.append(word[0] + "*"*(len(word)-2) + word[-1])
        else:
            result.append(word)
    return " ".join(result)
# -------------------------------------------------------


