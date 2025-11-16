initial_prompt = '''Instructions for answering:
1. Read each question carefully.
2. Review the story to find the relevant information.
3. If the information is not explicitly stated in the story, respond with the most logical answer based on the given information or one that can be inferred upon.
'''

new_prompt = '''Instructions for answering:
1. Read each question carefully.
2. Review the story to find the relevant information.
3. If the information is not explicitly stated in the story, respond with the most logical answer based on the given information or one that can be inferred upon.
4. If the information was neither explicitly nor implicitly mentioned, answer "Not mentioned in the text or story." Do not hallucinate.
'''

def replace_prompt(initial: str, new: str, quiz: str) -> str:
    return quiz.replace(initial, new, 1)

def copy2new_prompt_file(input_quiz_path: str):
    with open(input_quiz_path, 'r') as file:
        quiz = file.read()
    
    new_quiz = replace_prompt(initial_prompt, new_prompt, quiz)

    output_quiz_path = input_quiz_path.replace(".txt", "_no_hallucination.txt")
    with open(output_quiz_path, 'w') as file:
        file.write(new_quiz)


if __name__ == "__main__":
    for i in range(10):
        for j in range(10):
            copy2new_prompt_file(
                 f"texts/la_comédie_humaine_(balzac)/contracted/temp_injected_facts/272k_length_{(i+1)*10}%_factloc_{j*10+5}.txt"
            )
