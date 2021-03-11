from django.contrib import admin

from .models import Person, Invite
from .models import TestStep, TestSummary
from .models import Question, Answer, CurrentAnswers, ChallengeSummary


admin.site.register(Person)
admin.site.register(Invite)
admin.site.register(TestStep)
admin.site.register(TestSummary)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(CurrentAnswers)
admin.site.register(ChallengeSummary)
