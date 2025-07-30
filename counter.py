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
    "pg1941_Letters_of_Two_Brides",
    "pg1481_A_Daughter_of_Eve",
    "pg1950_A_Woman_of_Thirty",
    "pg1729_The_Deserted_Woman",
    "pg1428_La_Grenadiere",
    "pg1189_The_Message",
    "pg1389_Gobseck",
    "pg1556_A_Marriage_Contract",
    "pg1403_A_Start_in_Life",
    "pg1482_Modeste_Mignon",
    "pg1957_Beatrix",
    "pg1683_Honorine",
    "pg1954_Colonel_Chabert",
    "pg1220_The_Atheist's_Mass",
    "pg1410_The_Commission_in_Lunacy",
    "pg1230_Pierre_Grassou",
    "pg1715_Eugenie_Grandet",
    "pg7927_The_Celibates",
    "pg1345_The_Vicar_of_Tours",
    "pg1380_The_Two_Brothers",
    "pg1474_The_Illustrious_Gaudissart",
    "pg1912_The_Muse_of_the_Department",
    "pg1352_An_Old_Maid",
    "pg1405_The_Collection_of_Antiquities",
    "pg1569_The_Lily_of_the_Valley"
]



count_words_and_tokens_for_list([f"texts/la_comédie_humaine_(balzac)/original/{story}.txt"
                                 for story in stories])