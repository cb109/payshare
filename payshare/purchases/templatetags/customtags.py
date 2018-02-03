from django import template

register = template.Library()


@register.filter(name="addclass")
def addclass(value, arg):
    """Use this tag to add a CSS class e.g. to a form element."""
    return value.as_widget(attrs={"class": arg})
