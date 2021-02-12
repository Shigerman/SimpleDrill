# simpledrill
A service to learn programming based on exercise repetition.

### screens layout
Homepage screen elements:
* 'Register' button
* 'Login' button
* 'Drill' button
* 'Take the test' button

Drilling screen elements:
* question and explanation texts
* four answers
* 'D/Q' button meaning 'I don't know'
* 'N/A' button meaning 'no correct options available'
* 'End' button, which returns to the homepage screen
* 'Next question' button (to implement later)

Explain test screen elements:
* Test process or result explanation
* 'Take the test' button

Test screen elements:
* question
* answer field
* 'Submit' button

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
