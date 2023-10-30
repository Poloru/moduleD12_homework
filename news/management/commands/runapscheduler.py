import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from django.utils import timezone
import datetime

from news.models import Category, Post

logger = logging.getLogger(__name__)


def weekly_notice():
    """Weekly notification of the latest news by subscribed categories"""
    categories = Category.objects.all()
    posts = Post.objects.all()
    start_date = timezone.now() - datetime.timedelta(weeks=1)
    subs_news_result_list = {}

    for cat in categories:
        subscribers = cat.subscribers.all()
        if len(subscribers) > 0:
            weekly_news = posts.filter(
                postCategory__name=cat,
                dateCreation__gte=start_date,
            )

            for sub in subscribers:
                if sub not in subs_news_result_list:
                    subs_news_result_list[sub] = []
                subs_news_result_list[sub].extend(weekly_news)

    subs_news_result_list[sub] = set(subs_news_result_list[sub])

    for sub, posts in subs_news_result_list.items():
        html_content = render_to_string(
            template_name='mail/weekly_notice.html',
            context={
                'user': sub,
                'posts': posts,
            },
        )
        msg = EmailMultiAlternatives(
            subject=f'Недельные новости NewsPort',
            body='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[sub.email],
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            weekly_notice,
            trigger=CronTrigger(second="*/10"),  # Включение для теста
            # trigger=CronTrigger(
            #     day_of_week="mon", hour="00", minute="00"
            # ),
            id="weekly_notice",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_notice'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить,
            # либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")


# # наша задача по выводу текста на экран
# def my_job():
#     #  Your job processing logic here...
#     print('hello from job')


# def my_job():
#     send_mail(
#         'Job mail',
#         'hello from job!',
#         from_email='peterbadson@yandex.ru',
#         recipient_list=['skavik46111@gmail.com'],
#     )

