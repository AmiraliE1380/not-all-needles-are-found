from inject_fact import inject_fact
from call_api import chat_with_model
from take_quiz_batch import get_unique_path, construct_single_quiz
import os

import time

# model = "gpt-5"  # default model to use for chat_with_model
model = "gemini-2.5-flash"  # default model to use for chat_with_model
grading_model = "gpt-5-mini"  # model to use for grading
max_context_length = 1000 # number of thousands of tokens


MIDDLE_OF_STORY = (
"\n################################################"
"\n############# MIDDLE OF THE STORY. #############"
"\n################################################\n"
)


def grade_quiz(model_response, ground_truth):
    """
    Returns for numbers in the interval [0, 100] representing the percentage of correct answers.
    The four numbers represent:
    Total grade
    direct facts 
    inferential facts
    hallucination
    """

    print(f"Grading model_responce = \n{model_response}\n")
    print(f"With ground_truth = \n{ground_truth}\n")

    grading_prompt_address = 'prompts/grading.txt'
    with open(grading_prompt_address, 'r') as file:
        grading_prompt = file.read()

    grading_prompt = grading_prompt.format(MODEL_RESPONSE=model_response, GROUND_TRUTH=ground_truth)
    scores = chat_with_model(prompt=grading_prompt, model=grading_model)
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
    


# def take_single_quiz(story_address, fact_location : float):
#     """
#     Main function to take a quiz by injecting facts into a story and grading the model's responses.
#     """

#     # load questions
#     with open('prompts/questions/questions1.txt', 'r') as file:
#         questions = file.read()

#     # load prompt
#     with open('prompts/quiz.txt', 'r') as file:
#         prompt = file.read()

#     with open('prompts/facts/facts1.txt', 'r') as file:
#         facts = file.read()

#     # load story
#     # story_address = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_1000_actual_1244.txt"
#     # story_address = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_100%.txt"
#     with open(story_address, 'r', encoding='utf-8') as file:
#         story = file.read()

#     print(f"story length in words: {len(story.split())}")
#     # print(f"facts = \n{facts}\n")

#     story = inject_fact(facts, story, fact_location) 
#     quiz = prompt.format(STORY=story, QUESTIONS=questions)

#     # print(f"quiz = \n{quiz}\n")

#     model_responce = chat_with_model(prompt=quiz, model=model)
#     # print(f"model_responce = \n{model_responce}\n")

#     with open('prompts/answer_keys/answer_key1.txt', 'r') as file:
#         ground_truth = file.read()
#     # print(f"ground_truth = \n{ground_truth}\n")

#     grade = grade_quiz(model_responce, ground_truth)
#     print(f"Grade = {grade}\n")

#     return grade




def take_quizes_diff_lengths():
    """
    takes quiz using contracted stories with 10 different lengths,
    128k, ..., 12k.
    Also injects facts at different locations in the story
    from 0.1 to 0.9 with step 0.1.
    """
    
    # for i in range(10):
    # for i in range(8,10):
    for i in [1,2,3,8,9]:
        story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_{max_context_length}k_expected_{(i+1)*10}%.txt"
        # grades.append([])
        # for j in [9]:

        for hallucination_version in [
                                      "",
                                      "_no_hallucination"
                                      ]:
            for j in range(10):
            # for j in [9]:
                fact_location = j * 0.1 + 0.05
                print(f"Taking quiz for story length {(i+1)*10}% and fact location {fact_location*100:.0f}...")
                # grades[i - 1].append(take_single_quiz(story_address, fact_location))
                
                # cache quiz to avoid re-generating it
                id = f"{max_context_length}k_length_{(i+1)*10}%_factloc_{fact_location*100:.0f}"
                cached_quiz_dir = "texts/la_comédie_humaine_(balzac)/contracted/temp_injected_facts"
                # cached_quiz_addr = cached_quiz_dir + f"/{id}.txt"
                # cached_quiz_addr = cached_quiz_dir + f"/{id}_no_hallucination.txt"
                cached_quiz_addr = cached_quiz_dir + f"/{id}{hallucination_version}.txt"

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

                response = chat_with_model(prompt=quiz, model=model)
                print(f"response: {response}\n")
                print("\n" + "="*50 + "\n")

                # save_results_path = f"logs/quiz_responses_{id}_{model}.txt"
                # save_results_path = f"logs/quiz_responses_{id}_{model}_no_hallucination.txt"
                save_results_path = f"logs/quiz_responses_{id}_{model}{hallucination_version}.txt"
                os.makedirs(os.path.dirname(save_results_path), exist_ok=True)

                save_results_path = get_unique_path(save_results_path)
                with open(save_results_path, 'w') as file:
                    file.write(str(response))

                time.sleep(500)  # to avoid token rate per minute limit errors
        
    

def take_distributed_facts_quizzes():
    dist_fact_stories_addr = "texts/la_comédie_humaine_(balzac)/contracted/distributed"

    # load all stories with distributed facts
    story_files = os.listdir(dist_fact_stories_addr)
    for story_file in story_files:
        if str(max_context_length) not in story_file:
            continue
        
        story_address = os.path.join(dist_fact_stories_addr, story_file)
        print(f"Taking quiz for story {story_file}...")
        
        # cache quiz to avoid re-generating it
        id = story_file.replace(".txt", "")
        cached_quiz_dir = "texts/la_comédie_humaine_(balzac)/contracted/temp_distributed_facts"

        # take both versions of the quiz: with and without hallucination instruction
        for hallucination_version in [
                                    #   "",
                                      "_no_hallucination"
                                      ]:
            if "200k_distributed_arcsine" not in id:
                continue


            cached_quiz_addr = cached_quiz_dir + f"/{id}{hallucination_version}.txt"

            if os.path.exists(cached_quiz_addr):
                with open(cached_quiz_addr, 'r', encoding='utf-8') as file:
                    quiz = file.read()
                print(f"Loaded cached quiz from {cached_quiz_addr}")
            else:
                # determine fact location based on distribution name
                
                quiz = construct_single_quiz(story_address, -1, hallucination_version != "")
                quiz = quiz.replace(MIDDLE_OF_STORY, '\n')
                os.makedirs(cached_quiz_dir, exist_ok=True)
                with open(cached_quiz_addr, 'w', encoding='utf-8') as file:
                    file.write(quiz)
                print(f"Saved constructed quiz to {cached_quiz_addr}")

            response = chat_with_model(prompt=quiz, model=model)
            print(f"response: {response}\n")
            print("\n" + "="*50 + "\n")

            time.sleep(350)  # to avoid token rate per minute limit errors

            save_results_path = f"logs/quiz_responses_{id}_{model}{hallucination_version}.txt"
            os.makedirs(os.path.dirname(save_results_path), exist_ok=True)

            save_results_path = get_unique_path(save_results_path)
            with open(save_results_path, 'w') as file:
                file.write(str(response))
        
        

if __name__ == "__main__":
    take_quizes_diff_lengths()
    # take_distributed_facts_quizzes()