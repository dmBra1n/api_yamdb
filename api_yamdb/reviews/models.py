import datetime

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, default='')
    genres = models.ManyToManyField(Genre, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(year__lte=datetime.datetime.now().year),
                name='check_year_lte_current_year',
            )
        ]
