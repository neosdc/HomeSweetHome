from django import template
from bookshelf.models import Book
register = template.Library()

@register.filter
def replace_bookpath(value):
    return value.replace(Book.BOOKS_PATH, '') if value is not None else value
