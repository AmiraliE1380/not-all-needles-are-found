from inject_fact import inject_fact
from call_api import chat_with_model


def grade_quiz(model_responce, ground_truth):
    """
    Grade the quiz based on the model's responses and the ground truth answers.
    
    Args:
        model_responce (str): The model's responses to the quiz questions.
        ground_truth (str): The correct answers to the quiz questions.
    
    Returns:
        int: The grade (number of correct answers).
    """
    def _exatract_answer(line):
        # Extract the answer from a line like "Question 1: A"
        return line.split(':')[-1].strip()

    model_answers = [line.strip() for line in model_responce.split('\n') if line.strip()]
    correct_answers = [line.strip() for line in ground_truth.split('\n') if line.strip()]
    
    grade = sum(1 for ma, ca in zip(model_answers, correct_answers) if ma == ca)
    
    return grade / len(correct_answers) * 100  

# test grade_quiz function
print(grade_quiz(model_responce="Question 1: A\nQuestion 2: C\nQuestion 3: C\nQuestion 4: D", 
                 ground_truth="Question 1: A\nQuestion 2:  C  \nQuestion 3: C\nQuestion 4: D"))  # Expected output: 4
exit()

# load questions
with open('prompts/questions1.txt', 'r') as file:
    questions = file.readlines()

# load prompt
with open('prompts/quiz.txt', 'r') as file:
    prompt = file.read()

with open('prompts/facts1.txt', 'r') as file:
    facts = file.readlines()

# load story
story_address = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_1000_actual_1244.txt"
with open(story_address, 'r', encoding='utf-8') as file:
    story = file.read()

story = inject_fact(facts, story, 0.5) 
quiz = prompt.format(story=story, questions=''.join(questions))

model_responce = chat_with_model(prompt=quiz)
print(f"model_responce = \n{model_responce}\n")

with open('prompts/ground_truth1.txt', 'w') as file:
    ground_truth = file.read()
print(f"ground_truth = \n{ground_truth}\n")

grade_quiz = grade_quiz(model_responce, ground_truth)
print(f"Grade = {grade_quiz}\n")

