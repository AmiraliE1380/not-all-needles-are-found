import tiktoken


def count_words_and_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    word_count = len(text.split())
    # Use tiktoken for token counting (OpenAI tokenizer, e.g. for GPT-3.5/4)
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_count = len(enc.encode(text))

    print(f"file: {file_path}")
    print(f"Word count: {word_count}")
    print(f"Token count: {token_count}")

    return word_count, token_count

def count_words_and_tokens_for_list(file_paths):
    word_count_sum, token_count_sum = 0, 0
    
    for file_path in file_paths:
        word_count, token_count = count_words_and_tokens(file_path)
        word_count_sum += word_count
        token_count_sum += token_count

    print("\nTotal counts for all files:")
    print(f"Total Word count: {word_count_sum}")
    print(f"Total Token count: {token_count_sum}")

# Example usage:
stories = [
    "pg1680_At_the_Sign_of_the_Cat_and_Racket",
    "pg1305_The_Ball_at_Sceaux",
    "pg1196_The_Purse",
    "pg1374_Vendetta",
    "pg1357_Madame_Firmiani",
    "pg1810_A_Second_Home",
    "pg1411_Domestic_Peace",
    "pg1369_Paz_(La_Fausse_Maitresse)",
    "pg1373_Etude_de_femme",
    "pg1714_Another_Study_of_Woman",
    "pg1710_La_Grand_Breteche",
    "pg1898_Albert_Savarus",
    "pg1941_Letters_of_Two_Brides"
]


count_words_and_tokens_for_list([f"texts/la_comédie_humaine_(balzac)/original/{story}.txt"
                                 for story in stories])