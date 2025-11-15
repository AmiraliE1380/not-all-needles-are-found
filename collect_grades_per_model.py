



if __name__ == "__main__":
    model = "gpt-5-mini"
    for i in range(10):
        for j in range(10):
            addr = f"logs/quiz_responses_400k_length_{(i+1)*10}%_factloc_{5+j*10}_{model}.txt"
            with open(addr, 'r') as file:
                graded_quiz = file.read()
            graded = grade(addr)