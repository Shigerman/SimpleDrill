from django.shortcuts import render


def homepage(request):
    context = {}
    return render(request, 'homepage.html', context)


def register_user(request):
    context = {}
    return render(request, 'register_user.html', context)
