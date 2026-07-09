# Long-Context NIAH / Quiz Pipeline

Run any script as: `python <file>.py` (no arguments)

Setup:
- Create venv + install deps (use your usual workflow)
- Put API keys in `.env`
- Adjust paths/defaults in `constant_vals.py`

Main workflow (run in order):
1) Contract corpus: `python contract_entire_story.py`
2) Inject facts (9 distributions): `python inject_fact.py`
3) Take quizzes (API + cache): `python take_quiz.py`
4) Grade outputs: `python grader.py`
