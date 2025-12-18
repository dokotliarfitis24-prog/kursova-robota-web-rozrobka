from django import template
from shop.firebase_models import Category

register = template.Library()


@register.simple_tag
def get_categories():
    return Category.get_all()



