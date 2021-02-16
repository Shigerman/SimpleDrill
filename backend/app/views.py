from django.shortcuts import render
from django.contrib.auth import login
from threadlocals.threadlocals import get_current_request
from .. import core


def homepage(request):
    context = {}
    return render(request, 'homepage.html', context)


def register_user(request):
    context = {}
    if username and password and invite:
        return core.user.User.register(username, password, invite)
    return render(request, 'register_user.html', context)


def connect_person_to_session(person):
    login(get_current_request(), person.user)


def render_register_user(request, invalid_code=False):
    username = request.GET.get('username')
    password = request.GET.get('password')
    invite = request.GET.get('invite')
    context = {'username': username, 'password': password, 'invite': invite}


def login_user(request):
    context = {}
    return render(request, 'login_user.html', context)


def select_topic(request):
    context = {}
    return render(request, 'select_topic.html', context)


def drill_topic(request):
    context = {}
    return render(request, 'drill_topic.html', context)


def explain_test(request):
    context = {}
    return render(request, 'explain_test.html', context)


def test(request):
    context = {}
    return render(request, 'test.html', context)



