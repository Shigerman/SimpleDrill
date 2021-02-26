from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from threadlocals.threadlocals import get_current_request

from backend import core
from .models import Person, Invite


def homepage(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    return render(request, 'homepage.html')


def render_homepage():
    context = {}
    return render(get_current_request(), 'homepage.html', context)


def register_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    invite = request.GET.get('invite')
    if username and password and invite:
        return core.visitor.Visitor.register(username, password, invite)
    return render(request, 'register_visitor.html')


def connect_person_to_session(person):
    login(get_current_request(), person.user)


def render_register_visitor(request, invalid_code=False):
    context = {"invalid_code": invalid_code}
    return render(get_current_request(), 'register_visitor.html', context)


def render_invites(invites):
    context = {'invites': invites,}
    return render(get_current_request(), 'view_invites.html', context)


def login_visitor(request):
    return render(request, 'login_visitor.html')


def render_login_visitor(request, invalid_credentials=False):
    context = {"invalid_credentials": invalid_credentials}
    return render(request, 'login_visitor.html', context)


def logout_visitor(request):
    if request.user.is_authenticated:
        logout(get_current_request(), person.visitor)
    return render(request, 'login_visitor.html', {})


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



