from django.contrib import admin

from .models import Invite, Person
from .models import TestStep, TestSummary
from .models import Question, Answer, CurrentAnswers, ChallengeSummary


admin.site.register(Invite)
admin.site.register(Person)
