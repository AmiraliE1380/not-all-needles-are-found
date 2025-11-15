from inject_fact import inject_fact
# from call_api import chat_with_model
from batch_api import run_chat_batch_and_get_results, BatchItem
from counter import count_tokens
# from take_quiz import grade_quiz
import os

import re

model = "gpt-5-mini"  # default model to use for chat_with_model
# model = "gpt-5-mini"  # default model to use for chat_with_model
grading_model = "gpt-5-mini"  # model to use for grading
max_context_length = 400 # number of thousands of tokens


def construct_single_quiz(story_address, fact_location : float) -> str:
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

    # print(f"facts = \n{facts}\n")

    story = inject_fact(facts, story, fact_location) 
    quiz = prompt.format(STORY=story, QUESTIONS=questions)

    print(f"quiz length in words: {len(quiz.split())}")
    print(f"quiz length in tokens: {count_tokens(quiz)}")
    # print(f"quiz = \n{quiz}\n")

    # model_responce = chat_with_model(prompt=quiz, model=model)
    # print(f"model_responce = \n{model_responce}\n")

    # with open('prompts/answer_keys/answer_key1.txt', 'r') as file:
    #     ground_truth = file.read()
    # print(f"ground_truth = \n{ground_truth}\n")

    # grade = grade_quiz(model_responce, ground_truth)
    # print(f"Grade = {grade}\n")

    return quiz



def get_unique_path(path: str) -> str:
    """
    Return a path that does not exist by appending or incrementing a numeric suffix
    before the extension, e.g. file.txt -> file_1.txt, file_1.txt -> file_2.txt, etc.
    """
    if not os.path.exists(path):
        print(f"Writing to {path}...")
        return path

    base, ext = os.path.splitext(path)
    m = re.match(r"^(.*)_(\d+)$", base)
    if m:
        root = m.group(1)
        idx = int(m.group(2)) + 1
    else:
        root = base
        idx = 1

    candidate = f"{root}_{idx}{ext}"
    while os.path.exists(candidate):
        idx += 1
        candidate = f"{root}_{idx}{ext}"
    
    print(f"Writing to {candidate}...")
    return candidate


def take_quizes_diff_lengths():
    """
    takes quiz using contracted stories with 10 different lengths,
    128k, ..., 12k.
    Also injects facts at different locations in the story
    from 0.1 to 0.9 with step 0.1.
    """
    batch_items = []
    
    # for i in range(10):
    for i in [0]:
        story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_{max_context_length}k_expected_{(i+1)*10}%.txt"
        # grades.append([])
        # for j in range(10):
        for j in [0]:
            fact_location = j * 0.1 + 0.05
            print(f"Taking quiz for story length {(i+1)*10}% and fact location {fact_location}...")
            # grades[i - 1].append(take_single_quiz(story_address, fact_location))
            
            # cache quiz to avoid re-generating it
            id = f"{max_context_length}k_length_{(i+1)*10}%_factloc_{fact_location*100:.0f}"
            cached_quiz_dir = "texts/la_comédie_humaine_(balzac)/contracted/temp_injected_facts"
            cached_quiz_addr = cached_quiz_dir + f"/{id}.txt"

            if os.path.exists(cached_quiz_addr):
                with open(cached_quiz_addr, 'r', encoding='utf-8') as file:
                    quiz = file.read()
                print(f"Loaded cached quiz from {cached_quiz_addr}")
            else:
                quiz = construct_single_quiz(story_address, fact_location)
                os.makedirs(cached_quiz_dir, exist_ok=True)
                with open(cached_quiz_addr, 'w', encoding='utf-8') as file:
                    file.write(quiz)
                print(f"Saved constructed quiz to {cached_quiz_addr}")
            
            batch_items.append(
                BatchItem(
                    custom_id=id,
                    prompt=quiz,
                    model=model,
                )
            )
            print("\n" + "="*50 + "\n")

            # time.sleep(1)  # to avoid rate limit errors
    
    print(f"Running batch of {len(batch_items)} quiz items...")
    results = run_chat_batch_and_get_results(problem_id=model,
                                             items=batch_items, 
                                             default_model=model)
    print(f"Results: {results}\n")
    print("Batch results obtained.")

    save_results_path = f"logs/batch_results_{model}.txt"
    os.makedirs(os.path.dirname(save_results_path), exist_ok=True)

    save_results_path = get_unique_path(save_results_path)
    with open(save_results_path, 'w') as file:
        file.write(str(results))

    # print(f"Grades saved to {save_grades_path}")
    # print("Grades matrix:")
    # print(grades)
    # plot_grades(grades)
    # plot_grades([[0, 20.5],[90.8,10]])
    

if __name__ == "__main__":
    take_quizes_diff_lengths()