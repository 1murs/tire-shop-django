from pathlib import Path
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def image_exists(image_field):
    if not image_field:
        return False
    return (Path(settings.MEDIA_ROOT) / str(image_field)).exists()
