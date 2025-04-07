from django import template

register = template.Library()

@register.filter()
def rupiah(value):
    try:
        value = int(value)
        return "Rp {:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value