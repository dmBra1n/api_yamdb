import csv

from django.db.models import Model
from django.core.exceptions import ObjectDoesNotExist

from api_yamdb.settings import STATICFILES_DIRS
from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment

DATA_DIR = STATICFILES_DIRS[0] / 'data/'

ENCODING = 'utf-8'


def get_file_path(file_name: str):
    return DATA_DIR / file_name


def import_dictionary(model: Model, file_name: str):
    file_path = get_file_path(file_name)
    with open(file_path, encoding=ENCODING) as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                model.objects.update_or_create(id=row['id'], defaults=row)
            except Exception as e:
                print(f'Error importing into {model.__name__}: {e}')


def import_categories(file_name: str):
    import_dictionary(Category, file_name)


def import_genres(file_name: str):
    import_dictionary(Genre, file_name)


def import_users(file_name: str):
    import_dictionary(User, file_name)


def import_titles(file_name: str):
    file_path = get_file_path(file_name)
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
                print(f"Error importing into Title: {e}")


def import_title_genres(file_name: str):
    file_path = get_file_path(file_name)
    with open(file_path, encoding=ENCODING) as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                title = Title.objects.get(id=row['title_id'])
                genre = Genre.objects.get(id=row['genre_id'])
            except ObjectDoesNotExist:
                continue

            title.genres.add(genre)


def import_reviews(file_name: str):
    file_path = get_file_path(file_name)
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
                print(f"Error importing into Review: {e}")


def import_comments(file_name: str):
    file_path = get_file_path(file_name)
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
                Comment.objects.update_or_create(id=row['id'], defaults=row)
            except Exception as e:
                print(f"Error importing into Comment: {e}")


if __name__ == '__main__':

    import_categories('category.csv')
    import_genres('genre.csv')
    import_users('users.csv')
    import_titles('titles.csv')
    import_title_genres('genre_title.csv')
    import_reviews('review.csv')
    import_comments('comments.csv')
