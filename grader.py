from take_quiz_batch import grade_quiz, get_unique_path

import re

grader_model = "gpt-5-mini"

def grade(response_addr : str):
    with open(response_addr, 'r') as file:
        text = file.read()

    pattern = re.compile(r'^\[([^\]]+)\]\s*$', re.MULTILINE)
    matches = list(pattern.finditer(text))

    responses: dict[str, str] = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        responses[m.group(1)] = content
    
    print(f"responses = {responses}\n")
    
    ground_truth_addr="prompts/answer_keys/answer_key1.txt"
    with open(ground_truth_addr, 'r') as file:
        ground_truth = file.read()

    grades: dict[str, list[int]] = {}
    for id, resp in responses.items():
        grade = grade_quiz(resp, ground_truth)
        print(f"Grade for {id} = {grade}\n")
        grades[id] = grade
    
    output_addr = response_addr.replace("batch_responses", "grades").replace(".txt", f"_{grader_model}_grades.txt")
    with open(get_unique_path(output_addr), 'w') as file:
        for id, grade in grades.items():
            file.write(f"{id} ==> {grade}\n")


if __name__ == "__main__":
    grade(
        response_addr="batch_responses/gpt-5-mini.txt"
    )
