from take_quiz import grade_quiz

import re

grader_model = "gpt-5-mini"

def grade(response_addr : str):
    with open(response_addr, 'r') as file:
        responses = file.read()

    # print(f"responses = {responses}\n")
    
    ground_truth_addr="prompts/answer_keys/answer_key1.txt"
    with open(ground_truth_addr, 'r') as file:
        ground_truth = file.read()

    grades = grade_quiz(responses, ground_truth)
    final_log = responses + f"\n\n=== GRADES ===\n\n{str(grades)}\n\n=== GRADES ===\n\n"
    grades_dict = {
        "total_scores" : grades[0], 
        "direct_scores" : grades[1],
        "inferential_scores" : grades[2],
        "hallucinations_scores" : grades[3]
    }
    final_log += str(grades_dict)
    
    output_addr = response_addr.replace(".txt", f"_grades.txt")
    with open(output_addr, 'w') as file:
        file.write(final_log)

    return grades


if __name__ == "__main__":
    model = 'gpt-4o-mini'
    for i in range(10):
        for j in range(10):
            addr = f"logs/quiz_responses_128k_length_{(i+1)*10}%_factloc_{5+j*10}_{model}"
            addr += "_no_hallucination.txt"
            print(f'Grading {addr}')
            print(grade(addr))
    