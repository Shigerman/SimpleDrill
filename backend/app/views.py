from django.shortcuts import render


def homepage(request):
    context = {}
    return render(request, 'homepage.html', context)


def register_user(request):
    username = request.GET.get('username')
    password = request.GET.get('password')
    invite = request.GET.get('invite')
    context = {'username': username,
               'password': password,
               'invite': invite}
    if email and password and invite:
        code_to_check = Invite.objects.get(code=invite)
        try:
            if not code_to_check.used_by:
                code_to_check.used_by = user.db
                code_to_check.save()
                return response
        except:  # need to add an exception here
            user = User.objects.register(username, password, invite)
            return render(request, 'register_user.html', {"invalid_code": True})
    return render(request, 'register_user.html', context)


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
