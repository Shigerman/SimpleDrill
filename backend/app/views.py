import urllib

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from threadlocals.threadlocals import get_current_request

from backend import core
from .models import Person, Invite


def homepage(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    return render(request, 'homepage.html')


def render_homepage(person):
    context = {}
    return render(get_current_request(), 'homepage.html', context)


def register_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    invite = request.GET.get('invite')

    if None in (username, password, invite):
        return render_register_visitor({})

    username = urllib.parse.unquote(username)
    password = urllib.parse.unquote(password)
    invite = urllib.parse.unquote(invite)

    if username and password and invite:
        return core.visitor.Visitor.register(username, password, invite)
    return render(request, 'register_visitor.html')


def connect_person_to_session(person):
    login(get_current_request(), person.user)


def disconnect_person_from_session(person):
    logout(get_current_request(), person.visitor)


def render_register_visitor(request, invalid_code=False):
    context = {"invalid_code": invalid_code}
    return render(get_current_request(), 'register_visitor.html', context)


def render_invites(invites):
    context = {'invites': invites,}
    return render(get_current_request(), 'view_invites.html', context)


def view_invites(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    visitor = core.Visitor(user=request.user)
    return visitor.show_invites()


def add_invite(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    visitor = core.Visitor(user=request.user)
    comment = request.GET.get('comment')
    if not comment:
        return redirect("/view_invites")
    visitor.add_invite(comment=comment)
    return visitor.show_invites()


def login_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')

    if None in (username, password):
        return render_login_visitor(request)

    username = urllib.parse.unquote(username)
    password = urllib.parse.unquote(password)

    if username and password:
        return core.visitor.Visitor.login(username, password)
    return render(request, 'login_visitor.html')


def logout_visitor(request):
    if not request.user.is_authenticated:
        return redirect("/")
    visitor = core.Visitor(user=request.user)
    return visitor.logout()


def render_login_visitor(request, invalid_credentials=False):
    context = {"invalid_credentials": invalid_credentials}
    return render(request, 'login_visitor.html', context)


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
