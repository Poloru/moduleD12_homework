from django.core.management.base import BaseCommand, CommandError

import news.models
from news.models import Post, Category


class Command(BaseCommand):
    help = 'Удаление всех постов из категории'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        answer = input(f'Вы правда хотите удалить все статьи в категории {options["category"]}? yes/no')
        if answer != 'yes':
            self.stdout.write(self.style.ERROR('Отменено'))
        else:
            try:
                category = Category.objects.get(name=options['category'])
                Post.objects.filter(postCategory=category).delete()
                self.stdout.write(self.style.SUCCESS(f'Успешно удалены все новости из категории: {category.name}'))
            except news.models.Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Не удалось найти категорию: {options["category"]}'))


# --------------------------------
# from sample_app.models import Product, Category

# category = Category.get(name=options['category'])
# print('===ppp===', options['category'])
# Post.objects.filter(category == category).delete()
                # в случае неправильного подтверждения говорим, что в доступе отказано
            # except Post.DoesNotExist:
            # except self.model.DoesNotExist:
            #     self.stdout.write(self.style.ERROR(f'Could not find category {options["category"]}'))




