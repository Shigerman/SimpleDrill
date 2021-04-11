from __future__ import annotations
import urllib.parse

import django.contrib.auth
from django.shortcuts import render, redirect
from django.urls import reverse
from threadlocals.threadlocals import get_current_request

import backend.core
import backend.core.visitor
from .models import Person, Invite, TestSummary


def need_logged_in_visitor(handler):
    def decorated(request):
        if not request.user.is_authenticated:
            return redirect(reverse("login-visitor"))
        visitor = backend.core.visitor.Visitor(user=request.user)
        return handler(request, visitor)
    return decorated


@need_logged_in_visitor
def homepage(_, visitor: backend.core.visitor.Visitor):
    return visitor.get_button_test_info()


def render_homepage(button_test_info: str):
    context = {'button_test_info': button_test_info}
    return render(get_current_request(), 'homepage.html', context)


def about(_):
    return render(get_current_request(), 'about.html')


def register_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    invite = request.GET.get('invite')
    credentials = (username, password, invite)

    if not any(credentials):
        return render_register_visitor()
    elif all(credentials):
        username = urllib.parse.unquote(username)
        password = urllib.parse.unquote(password)
        invite = urllib.parse.unquote(invite)
        return backend.core.visitor.Visitor.register(
            username, password, invite)
    else:
        return render_register_visitor(empty_field=True, invalid_code=False)


def render_register_visitor(
        empty_field: bool = False,
        invalid_code: bool = False):

    context = {
        "empty_field": empty_field,
        "invalid_code": invalid_code,
    }
    return render(get_current_request(), 'register_visitor.html', context)


def login_visitor(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    credentials = (username, password)

    if not any(credentials):
        return render_login_visitor()
    elif all(credentials):
        username = urllib.parse.unquote(username)
        password = urllib.parse.unquote(password)
        return backend.core.visitor.Visitor.login(username, password)
    else:
        return render_login_visitor(invalid_credentials=True)


def render_login_visitor(invalid_credentials: bool = False):
    context = {"invalid_credentials": invalid_credentials}
    return render(get_current_request(), 'login_visitor.html', context)


@need_logged_in_visitor
def logout_visitor(_, visitor: backend.core.visitor.Visitor):
    return visitor.logout()


def connect_person_to_session(person: Person):
    django.contrib.auth.login(get_current_request(), person.user)


def disconnect_person_from_session(_):
    django.contrib.auth.logout(get_current_request())


@need_logged_in_visitor
def add_invite(request, visitor: backend.core.visitor.Visitor):
    comment = request.GET.get('comment')
    if not comment:
        return redirect(reverse("view-invites"))
    visitor.add_invite(comment=comment)
    return visitor.show_invites()


@need_logged_in_visitor
def view_invites(_, visitor: backend.core.visitor.Visitor):
    return visitor.show_invites()


def render_invites(invites: Invite):
    context = {'invites': invites}
    return render(get_current_request(), 'view_invites.html', context)


@need_logged_in_visitor
def explain_test(_, visitor: backend.core.visitor.Visitor):
    return visitor.show_test_explanation()


def render_explain_test(
        explanation: backend.core.visitor.TestExplanationPage):
    context = {
        'foreword': explanation.foreword.split("\n"),
        'page_to_go_to': explanation.page_to_go_to,
        'btn_text': explanation.btn_text,
    }
    return render(get_current_request(), 'explain_test.html', context)


@need_logged_in_visitor
def select_topic(request, visitor: backend.core.visitor.Visitor):
    # user has to take the start test before drilling topics
    if not visitor.visitor_did_start_test():
        return redirect(reverse("explain-test"))
    topic = request.GET.get('topic')
    if topic:
        return visitor.want_to_drill(topic=topic)
    return render(request, 'select_topic.html')


@need_logged_in_visitor
def test(request, visitor: backend.core.visitor.Visitor):
    test_answer = request.GET.get('test_answer')
    if not test_answer:
        return visitor.show_test_step()
    return visitor.submit_test_answer(test_answer)


def render_test_step(test_step: TestSummary, countdown: str):
    context = {
        'test_question': test_step.test_question.test_question.split("\n"),
        'countdown': countdown,
    }
    return render(get_current_request(), 'test.html', context)


def render_test_score(test_score: tuple):
    start_score, final_score = test_score
    context = {
        'start_score': start_score,
        'final_score': final_score,
    }
    return render(get_current_request(), 'test.html', context)


@need_logged_in_visitor
def drill_topic(request, visitor: backend.core.visitor.Visitor):
    answer_choice = request.GET.get('choice')

    if request.GET.get('next') == "next":
        return visitor.get_next_challenge()
    elif answer_choice == 'dont_know':
        return backend.core.visitor.give_up_drill(visitor)
    elif answer_choice == 'no_correct_answer':
        return backend.core.visitor.submit_drill_answer(visitor,
            no_correct_answer=True)
    elif answer_choice:
        answer_id = int(answer_choice)  # need to get the answer as digit
        return backend.core.visitor.submit_drill_answer(visitor,
            answer_id=answer_id)
    return visitor.show_challenge()


def render_challenge(challenge: backend.core.visitor.Challenge,
        is_failure: bool = None, with_error: str = None):

    context = {
        'question': challenge.question.question_text.split("\n"),
        'answers': challenge.answers,
        'explanation': challenge.question.explanation_text.split("\n"),
        'disclose_answers': challenge.disclose_answers,
        'is_failure': is_failure,
        'error_msg': with_error,
    }
    return render(get_current_request(), 'drill_topic.html', context)
