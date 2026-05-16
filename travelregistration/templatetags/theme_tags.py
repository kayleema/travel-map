from django import template

register = template.Library()

AVAILABLE_THEMES = [
    {'code': 'light', 'name': 'Light'},
    {'code': 'dark', 'name': 'Dark'},
    {'code': 'parchment', 'name': 'Parchment'},
    {'code': 'sakura', 'name': 'Sakura'},
    {'code': 'hacker', 'name': 'Hacker'},
    {'code': 'neon', 'name': 'Neon'},
]


@register.simple_tag(takes_context=True)
def get_current_theme(context):
    request = context['request']
    return request.COOKIES.get('theme', 'light')


@register.simple_tag
def get_available_themes():
    return AVAILABLE_THEMES
