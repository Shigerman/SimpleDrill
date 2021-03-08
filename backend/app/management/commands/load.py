from importlib.resources import files
import json

from django.core import management
from django.core.management.base import BaseCommand
from backend.app.models import Answer, Question, TestStep

class Command(BaseCommand):
    help = "Clears database and loads new data into it"

    def handle(self, *args, **options):
        management.call_command('flush', verbosity=0, interactive=True)
        #management.call_command('loaddata', 'simpledrill_db.json', verbosity=0)

        files_to_load = files('backend.app.fixtures').glob('*.json')

        for file in files_to_load:
            if "test" in str(file):
                file = file.read_text()
                data = json.loads(file)
                for test_step in data:
                    TestStep(
                        test_question=test_step['q'],
                        topic=test_step['topic'],
                        test_answer=test_step['+'],).save()

            if "challenges" in str(file):
                file = file.read_text()
                data = json.loads(file)
                for challenge in data:
                    question = Question(
                        question_text=challenge['q'],
                        explanation_text=challenge['th'],
                        topic=challenge['topic'])
                    question.save()

                    # there can be no correct answer not to prompt the user
                    if '+' in challenge:
                        for answer in challenge['+']:
                            Answer(
                                question=question,
                                answer_text=answer,
                                is_correct=True).save()

                    for answer in challenge['-']:
                        Answer(
                            question=question,
                            answer_text=answer,
                            is_correct=False).save()
        print('The database was seeded successfully!')
