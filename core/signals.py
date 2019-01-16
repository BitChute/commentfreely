from django.dispatch import Signal


# see example https://medium.freecodecamp.org/how-to-testing-django-signals-like-a-pro-c7ed74279311

signal_new_comment = Signal(providing_args=['data'])

signal_update_comment = Signal(providing_args=['data'])

signal_delete_comment = Signal(providing_args=['data'])

signal_vote = Signal(providing_args=['data'])