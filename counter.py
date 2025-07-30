import tiktoken

story = "texts/original/pg1257_The_three_musketeers.txt"  # Replace with your .txt file path

def count_words_and_tokens(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    word_count = len(text.split())
    # Use tiktoken for token counting (OpenAI tokenizer, e.g. for GPT-3.5/4)
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    token_count = len(enc.encode(text))
    print(f"Word count: {word_count}")
    print(f"Token count: {token_count}")

count_words_and_tokens(story)