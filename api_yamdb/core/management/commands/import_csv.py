import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.models import Model

from api_yamdb.settings import STATICFILES_DIRS
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

DATA_DIR = STATICFILES_DIRS[0] / 'data/'

ENCODING = 'utf-8'


class Command(BaseCommand):
    help = 'Imports csv'

    def handle(self, *args, **options):
        self.import_categories('category.csv')
        self.import_genres('genre.csv')
        self.import_users('users.csv')
        self.import_titles('titles.csv')
        self.import_title_genres('genre_title.csv')
        self.import_reviews('review.csv')
        self.import_comments('comments.csv')

    def get_file_path(self, file_name: str):
        return DATA_DIR / file_name

    def import_dictionary(self, model: Model, file_name: str):
        file_path = self.get_file_path(file_name)
        with open(file_path, encoding=ENCODING) as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    model.objects.update_or_create(id=row['id'], defaults=row)
                except Exception as e:
                    self.stdout.write(
                        f'Error importing into {model.__name__}: {e}'
                    )

    def import_categories(self, file_name: str):
        self.import_dictionary(Category, file_name)

    def import_genres(self, file_name: str):
        self.import_dictionary(Genre, file_name)

    def import_users(self, file_name: str):
        self.import_dictionary(User, file_name)

    def import_titles(self, file_name: str):
        file_path = self.get_file_path(file_name)
        with open(file_path, encoding=ENCODING) as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    category = Category.objects.get(id=row['category'])
                except ObjectDoesNotExist:
                    continue

                row['category'] = category

                try:
                    Title.objects.update_or_create(id=row['id'], defaults=row)
                except Exception as e:
                    self.stdout.write(f"Error importing into Title: {e}")

    def import_title_genres(self, file_name: str):
        file_path = self.get_file_path(file_name)
        with open(file_path, encoding=ENCODING) as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                except ObjectDoesNotExist:
                    continue

                title.genre.add(genre)

    def import_reviews(self, file_name: str):
        file_path = self.get_file_path(file_name)
        with open(file_path, encoding=ENCODING) as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])
                except ObjectDoesNotExist:
                    continue

                row.pop('title_id')
                row['title'] = title
                row['author'] = author

                try:
                    Review.objects.update_or_create(id=row['id'], defaults=row)
                except Exception as e:
                    self.stdout.write(f"Error importing into Review: {e}")

    def import_comments(self, file_name: str):
        file_path = self.get_file_path(file_name)
        with open(file_path, encoding=ENCODING) as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])
                except ObjectDoesNotExist:
                    continue

                row.pop('review_id')
                row['review'] = review
                row['author'] = author

                try:
                    Comment.objects.update_or_create(
                        id=row['id'], defaults=row
                    )
                except Exception as e:
                    self.stdout.write(f"Error importing into Comment: {e}")
