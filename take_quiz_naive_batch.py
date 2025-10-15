from inject_fact import inject_fact
from call_api import chat_with_model
import os

import time

model = "gpt-5-mini"  # default model to use for chat_with_model
# model = "gpt-5"  # default model to use for chat_with_model

def grade_quiz(model_response, ground_truth):
    """
    Returns for numbers in the interval [0, 100] representing the percentage of correct answers.
    The four numbers represent:
    Total grade
    direct facts 
    inferential facts
    hallucination
    """

    # print(f"Grading model_responce = \n{model_response}\n")
    # print(f"With ground_truth = \n{ground_truth}\n")

    grading_prompt_address = 'prompts/grading.txt'
    with open(grading_prompt_address, 'r') as file:
        grading_prompt = file.read()

    grading_prompt = grading_prompt.format(MODEL_RESPONSE=model_response, GROUND_TRUTH=ground_truth)
    scores = chat_with_model(prompt=grading_prompt, model="gpt-5-mini")
    print(f"scores = \n{scores}\n") # scores are 30 numbers separated by a line break

    def _score_to_percentage(scores):
        return sum(scores) / len(scores) * 100

    scores = [int(score) for score in scores.split('\n')]
    total_scores = _score_to_percentage(scores)
    print(f"Total scores = {total_scores}")
    direct_scores = _score_to_percentage(scores[:10])
    print(f"Direct facts scores = {direct_scores}")
    inferential_scores = _score_to_percentage(scores[10:20])
    print(f"Inferential facts scores = {inferential_scores}")
    hallucinations_scores = _score_to_percentage(scores[20:])
    print(f"hallucinations scores = {hallucinations_scores}")

    return total_scores, direct_scores, inferential_scores, hallucinations_scores
    


def take_single_quiz(story_address, fact_location : float):
    """
    Main function to take a quiz by injecting facts into a story and grading the model's responses.
    """

    # load questions
    with open('prompts/questions/questions1.txt', 'r') as file:
        questions = file.read()

    # load prompt
    with open('prompts/quiz.txt', 'r') as file:
        prompt = file.read()

    with open('prompts/facts/facts1.txt', 'r') as file:
        facts = file.read()

    # load story
    # story_address = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_1000_actual_1244.txt"
    # story_address = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_100%.txt"
    with open(story_address, 'r', encoding='utf-8') as file:
        story = file.read()

    print(f"story length in words: {len(story.split())}")
    # print(f"facts = \n{facts}\n")

    story = inject_fact(facts, story, fact_location) 
    quiz = prompt.format(STORY=story, QUESTIONS=questions)

    # print(f"quiz = \n{quiz}\n")

    model_responce = chat_with_model(prompt=quiz, model=model)
    # print(f"model_responce = \n{model_responce}\n")

    with open('prompts/answer_keys/answer_key1.txt', 'r') as file:
        ground_truth = file.read()
    # print(f"ground_truth = \n{ground_truth}\n")

    grade = grade_quiz(model_responce, ground_truth)
    print(f"Grade = {grade}\n")

    return grade




def take_quizes_diff_lengths():
    """
    takes quiz using contracted stories with 10 different lengths,
    128k, ..., 12k.
    Also injects facts at different locations in the story
    from 0.1 to 0.9 with step 0.1.
    """
    grades = []
    
    # print(chat_with_model(prompt="Hello, this is a test to check if the model is working.", model=model))
    # time.sleep(300)  # to avoid rate limit errors
    
    for i in range(10):
    # for i in range(4, 10):
        story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_400k_expected_{(i+1)*10}%.txt"
        # story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_{(i+1)*10}%.txt"

        grades.append([])
        # for j in range(10):
        for j in range(10):
            fact_location = j * 0.1 + 0.05
            print(f"Taking quiz for story length {(i+1)*10}% and fact location {fact_location}...")
            grades[i].append(take_single_quiz(story_address, fact_location))
            # grades[i - 4].append(take_single_quiz(story_address, fact_location))
            print("\n" + "="*50 + "\n")

            time.sleep(300)  # to avoid rate limit errors
    
    print(grades)
    save_grades_path = f"logs/grades_{model}.txt"
    os.makedirs(os.path.dirname(save_grades_path), exist_ok=True)
    with open(save_grades_path, 'w') as file:
        file.write(str(grades))
    print(f"Grades saved to {save_grades_path}")
    # print("Grades matrix:")
    # print(grades)
    # plot_grades(grades)
    # plot_grades([[0, 20.5],[90.8,10]])
    

#####################################
# Batch processing of quizzes
#####################################


from batch_api import submit_chat_batch, wait_for_batch, BatchItem
def take_quizes_diff_lengths_batch():
    """
    Takes quizzes using contracted stories with 10 different lengths,
    128k, ..., 12k.
    Also injects facts at different locations in the story
    from 0.1 to 0.9 with step 0.1.
    Uses batch processing to submit the quizzes.
    """
    items = []
    
    for i in range(10):
        story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_400k_expected_{(i+1)*10}%.txt"
        # story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_{(i+1)*10}%.txt"

        for j in range(10):
            fact_location = j * 0.1 + 0.05
            print(f"Preparing quiz for story length {(i+1)*10}% and fact location {fact_location}...")
            items.append(BatchItem(
                custom_id=f"quiz_{i+1}_{j+1}",
                prompt=take_single_quiz(story_address, fact_location),
                system_prompt="You are a quiz grader."
            ))
    
    print(f"Submitting {len(items)} quizzes to batch processing...")
    batch = submit_chat_batch(items, default_model=model)
    
    print(f"Batch submitted with ID: {batch.id}")
    
    # Wait for the batch to complete
    final_batch = wait_for_batch(batch.id)
    
    print(f"Batch completed with status: {final_batch.status}")


if __name__ == "__main__":
    # # test grade_quiz function
    # print(grade_quiz(model_responce="Question 1: A\nQuestion 2: C\nQuestion 3: C\nQuestion 4: D", 
    #                  ground_truth="Question 1: A\nQuestion 2:  D  \nQuestion 3: C\nQuestion 4: D"))  # Expected output: 4
    # exit()
    
    # take_single_quiz()
    # take_quizes_diff_lengths()
    take_quizes_diff_lengths_batch()