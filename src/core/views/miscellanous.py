from django.shortcuts import redirect


def index(request):
    """ Redirect from main page to swagger """
    return redirect('/swagger')
