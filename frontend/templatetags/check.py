from django import template

register = template.Library()

@register.simple_tag
def is_checked(dic, key, filters):
    d = dict(dic).get(key)
    if d:
        if str(filters) in d:
            return True
    else:
        pass