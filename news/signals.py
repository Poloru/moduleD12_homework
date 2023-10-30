import logging

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post, PostCategory
from .tasks import new_post_subscription


# logger = logging.getLogger("django")


@receiver(m2m_changed, sender=PostCategory)
def notify_subscribers(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        new_post_subscription(instance)

    # logger.info("===kwargs11111111-===: ")
