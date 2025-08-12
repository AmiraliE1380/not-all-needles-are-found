from inject_fact import inject_fact
from call_api import chat_with_model

import time



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

    model_responce = chat_with_model(prompt=quiz)
    # print(f"model_responce = \n{model_responce}\n")

    with open('prompts/answer_keys/answer_key1.txt', 'r') as file:
        ground_truth = file.read()
    # print(f"ground_truth = \n{ground_truth}\n")

    grade = grade_quiz(model_responce, ground_truth)
    print(f"Grade = {grade}\n")

    return grade


def plot_grades(grades, save_path="heatmaps/heatmap.png"):
    """
    Render a numeric matrix (0–100) as a heat-map and save it to *save_path*.
    Each cell shows the value as a percentage with one decimal (e.g. 91.0%).
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # --- colour map: white → deep red -----------------------------------------
    cmap = LinearSegmentedColormap.from_list(
        "white_to_red",
        ["#f9f9f9", "#f2c9c9", "#ee9a9a", "#e55e5e", "#cc2929", "#640000"],
        N=256,
    )

    # --- build string matrix like "91.0%" -------------------------------------
    annot_strings = np.vectorize(lambda x: f"{x:.1f}%")(grades)

    # --- draw -----------------------------------------------------------------
    plt.figure(figsize=(len(grades), len(grades[0])), dpi=100)
    sns.heatmap(
        grades,
        vmin=0,
        vmax=100,
        cmap=cmap,
        square=True,
        linewidths=0.5,
        cbar_kws={"label": "Grade"},
        annot=annot_strings,   # use the strings with "%"
        fmt=""                 # disable seaborn's automatic formatting
    )
    plt.title("Grades Heat-map")

    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"Heat-map written to: {save_path}")




def take_quizes_diff_lengths():
    """
    takes quiz using contracted stories with 10 different lengths,
    128k, ..., 12k.
    Also injects facts at different locations in the story
    from 0.1 to 0.9 with step 0.1.
    """
    grades = []
    
    # for i in range(1, 11):
    for i in [10]:
        story_address = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_{i*10}%.txt"
        grades.append([])
        # for j in range(10):
        for j in range(10):
            fact_location = j * 0.1 + 0.05
            print(f"Taking quiz for story length {i*10}% and fact location {fact_location}...")
            # grades[i - 1].append(take_single_quiz(story_address, fact_location))
            grades[0].append(take_single_quiz(story_address, fact_location))
            print("\n" + "="*50 + "\n")

            time.sleep(1)  # to avoid rate limit errors
    
    # print("Grades matrix:")
    # print(grades)
    # plot_grades(grades)
    # plot_grades([[0, 20.5],[90.8,10]])
    

if __name__ == "__main__":
    # # test grade_quiz function
    # print(grade_quiz(model_responce="Question 1: A\nQuestion 2: C\nQuestion 3: C\nQuestion 4: D", 
    #                  ground_truth="Question 1: A\nQuestion 2:  D  \nQuestion 3: C\nQuestion 4: D"))  # Expected output: 4
    # exit()
    
    # take_single_quiz()
    take_quizes_diff_lengths()