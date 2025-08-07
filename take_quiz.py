from inject_fact import inject_fact

# load questions
with open('prompts/questions1.txt', 'r') as file:
    questions = file.readlines()

# load prompt
with open('prompts/quiz.txt', 'r') as file:
    prompt = file.read()

# load story
story_address = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_1000_actual_1244.txt"
with open(story_address, 'r', encoding='utf-8') as file:
    story = file.read()

