from django import template

register = template.Library()


@register.filter
def clp(valor):
    try:
        numero = int(valor)
        return f"${numero:,}".replace(",", ".")
    except (ValueError, TypeError):
        return valor
