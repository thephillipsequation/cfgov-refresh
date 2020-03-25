from django.db import models

from v1.atomic_elements import organisms


class Banner(models.Model):
    title = models.CharField(max_length=255,
            verbose_name='Banner title (internal reference only)',)
    banner = organisms.Banner
    #todo: add regex pattern for url matching and "enabled" toggle
