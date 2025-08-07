import tiktoken


def count_tokens(text):
    """Count the number of tokens in a given text using the OpenAI tokenizer."""
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(enc.encode(text))


def count_words_and_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    word_count = len(text.split())
    # Use tiktoken for token counting (OpenAI tokenizer, e.g. for GPT-3.5/4)
    token_count = count_tokens(text)

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

if __name__ == "__main__":
    # Example usage:
    from constant_vals import stories

    count_words_and_tokens_for_list([f"texts/la_comédie_humaine_(balzac)/preprocessed/{story}_cleaned.txt"
                                    for story in stories])

    # count_words_and_tokens("texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_expected_128000_actual_116530.txt")
    # # file: texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_expected_128000_actual_116530.txt
    # # Word count: 116530
    # # Token count: 154955


    # count_words_and_tokens("texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_expected_128000_actual_154955.txt")
