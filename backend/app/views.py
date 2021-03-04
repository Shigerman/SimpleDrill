import urllib

import django.contrib.auth
from django.shortcuts import render, redirect
from threadlocals.threadlocals import get_current_request

from backend import core
from .models import Person, Invite


def homepage(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    return render(request, 'homepage.html')


def register_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    invite = request.GET.get('invite')
    credentials = (username, password, invite)

    if any(credentials) and not all(credentials):
        return render_register_visitor(empty_field=True, invalid_code=False)
    elif all(credentials):
        username = urllib.parse.unquote(username)
        password = urllib.parse.unquote(password)
        invite = urllib.parse.unquote(invite)
        return core.Visitor.register(username, password, invite)
    return render(request, 'register_visitor.html')


def render_register_visitor(empty_field=False, invalid_code=False):
    context = {
        "empty_field": empty_field,
        "invalid_code": invalid_code,
        }
    return render(get_current_request(), 'register_visitor.html', context)


def login_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    credentials = (username, password)

    if any(credentials) and not all(credentials): 
        return render_login_visitor(invalid_credentials=True)
    elif all(credentials):
        username = urllib.parse.unquote(username)
        password = urllib.parse.unquote(password)
        return core.Visitor.login(username, password)
    return render(request, 'login_visitor.html')


def render_login_visitor(invalid_credentials=False):
    context = {"invalid_credentials": invalid_credentials}
    return render(get_current_request(), 'login_visitor.html', context)


def logout_visitor(request):
    if not request.user.is_authenticated:
        return redirect("/")
    visitor = core.Visitor(user=request.user)
    return visitor.logout()


def connect_person_to_session(person):
    django.contrib.auth.login(get_current_request(), person.user)


def disconnect_person_from_session(person):
    django.contrib.auth.logout(get_current_request())


def add_invite(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    visitor = core.Visitor(user=request.user)
    comment = request.GET.get('comment')
    if not comment:
        return redirect("view_invites")
    visitor.add_invite(comment=comment)
    return visitor.show_invites()


def view_invites(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    visitor = core.Visitor(user=request.user)
    return visitor.show_invites()


def render_invites(invites):
    context = {'invites': invites}
    return render(get_current_request(), 'view_invites.html', context)


def select_topic(request):
    context = {}
    return render(request, 'select_topic.html', context)


def drill_topic(request):
    context = {}
    return render(request, 'drill_topic.html', context)


def explain_test(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    visitor = core.Visitor(user=request.user)
    return visitor.show_test_explanation_before_test()


def render_explain_test(test_explanation):
    context = {
        'explanation_text': test_explanation.text.split("\n"),
        'page_to_go_to': test_explanation.page_to_go_to
    }
    return render(get_current_request(), 'explain_test.html', context)


def test(request):
    if not request.user.is_authenticated:
        return redirect("/login_visitor")
    visitor = core.Visitor(user=request.user)
    test_answer = request.GET.get('test_answer')
    if not test_answer:
        return visitor.show_test_step()
    return visitor.submit_test_answer(test_answer)


def render_test_step(test_step):
    context = {'test_question': test_step.test_question.test_question.split("\n")}
    return render(get_current_request(), 'test.html', context)


def render_test_score(test_score):
    pass
