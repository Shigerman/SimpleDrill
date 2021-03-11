import urllib

import django.contrib.auth
from django.shortcuts import render, redirect
from threadlocals.threadlocals import get_current_request

from backend import core
from .models import Person, Invite


def need_logged_in_visitor(handler):
    def decorated(request):
        if not request.user.is_authenticated:
            return redirect("/login_visitor")
        visitor = core.Visitor(user=request.user)
        return handler(request, visitor)
    return decorated


@need_logged_in_visitor
def homepage(request, visitor):
    return render(request, 'homepage.html')


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
        return core.Visitor.register(username, password, invite)
    else:
        return render_register_visitor(empty_field=True, invalid_code=False)


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

    if not any(credentials):
        return render_login_visitor()
    elif all(credentials):
        username = urllib.parse.unquote(username)
        password = urllib.parse.unquote(password)
        return core.Visitor.login(username, password)
    else:
        return render_login_visitor(invalid_credentials=True)


def render_login_visitor(invalid_credentials=False):
    context = {"invalid_credentials": invalid_credentials}
    return render(get_current_request(), 'login_visitor.html', context)


@need_logged_in_visitor
def logout_visitor(request, visitor):
    return visitor.logout()


def connect_person_to_session(person):
    django.contrib.auth.login(get_current_request(), person.user)


def disconnect_person_from_session(person):
    django.contrib.auth.logout(get_current_request())


@need_logged_in_visitor
def add_invite(request, visitor):
    comment = request.GET.get('comment')
    if not comment:
        return redirect("view_invites")
    visitor.add_invite(comment=comment)
    return visitor.show_invites()


@need_logged_in_visitor
def view_invites(request, visitor):
    return visitor.show_invites()


def render_invites(invites):
    context = {'invites': invites}
    return render(get_current_request(), 'view_invites.html', context)


@need_logged_in_visitor
def explain_test(request, visitor):
    return visitor.show_test_explanation_before_test()


def render_explain_test(test_explanation):
    context = {
        'explanation_text': test_explanation.text.split("\n"),
        'page_to_go_to': test_explanation.page_to_go_to
    }
    return render(get_current_request(), 'explain_test.html', context)


@need_logged_in_visitor
def select_topic(request, visitor):
    # user must take the start test before drilling topics
    if not visitor.visitor_did_start_test():
        return redirect("/explain_test")
    topic = request.GET.get('topic')
    if topic:
        return visitor.want_to_drill(topic=topic)
    return render(request, 'select_topic.html')


@need_logged_in_visitor
def test(request, visitor):
    test_answer = request.GET.get('test_answer')
    if not test_answer:
        return visitor.show_test_step()
    return visitor.submit_test_answer(test_answer)


def render_test_step(test_step):
    context = {'test_question':
        test_step.test_question.test_question.split("\n")}
    return render(get_current_request(), 'test.html', context)


def render_test_score(test_score):
    start_score, final_score = test_score
    context = {
        'start_score': start_score,
        'final_score': final_score,
    }
    return render(get_current_request(), 'test.html', context)


@need_logged_in_visitor
def drill_topic(request, visitor):
    answer_choice = request.GET.get('choice')

    if request.GET.get('next') == "next":
        return core.Visitor.get_next_challenge(visitor)
    elif answer_choice == 'dont_know':
        return core.visitor.give_up_drill(visitor)
    elif answer_choice == 'no_correct_answer':
        return core.visitor.submit_drill_answer(visitor,
            no_correct_answer=True)
    elif answer_choice:
        answer_id = int(answer_choice) # need to get the answer as digit
        return core.visitor.submit_drill_answer(visitor, answer_id=answer_id)
    return visitor.show_challenge()


def render_challenge(challenge, is_failure=None, with_error=None):
    context = {
        'question': challenge.question.question_text,
        'answers': challenge.answers,
        'explanation': challenge.question.explanation_text,
        'disclose_answers': challenge.disclose_answers,
        'is_failure': is_failure,
        'error_msg': with_error,
    }
    return render(get_current_request(), 'drill_topic.html', context)
