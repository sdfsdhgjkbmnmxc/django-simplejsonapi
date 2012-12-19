ACTIONS_DICT = {}


def register_action(func):
    ACTIONS_DICT[func.__name__] = func
    return func


@register_action
def ping(**params):
    return 'pong'

