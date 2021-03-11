# simpledrill
A service to learn programming based on exercise repetition.

## instruments used
* Python and Django for backend
* Numl framework for frontend
* Poetry for virtual environment
* Pytest for testing

### screens layout
Homepage screen elements:
* 'Register' button
* 'Login' button
* 'Drill' button
* 'Take the test' button

Drilling screen elements:
* question and explanation texts
* four answers
* 'Help' button meaning 'I don't know'
* 'No correct answer' button meaning
* 'End' button, which returns to the 'select topic' screen
* 'Next question' button

Explain test screen elements:
* Test process or result explanation
* 'Take the test' button

Test screen elements:
* question
* answer field
* 'Submit' button
* "I don't know" button


### activity algorithms
* Correct answer >>> show correct answer and its explanation >>> next question
  (to implement later)
* Incorrect answer or "I don't know" answer >>> show correct answer and
  its explanation >>> next question (to implement later)


### testing the app
Command to run the tests:
```
poetry run python manage.py test backend
```

### creating admins
```
poetry rum python manage.py createsuperuser
poetry run python manage.py createperson
```
