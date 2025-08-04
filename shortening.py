# utility functions for text shortening
def count_words(s: str) -> int:
    # split() with no args splits on any whitespace and collapses multiple spaces
    return len(s.split())


def build_prompt(input_text: str, original_word_count: int, shrink_percent: int) -> str:
    target_word_count = round(original_word_count * (1 - shrink_percent / 100))

    with open("prompts/shortening.txt", "r", encoding="utf-8") as f:
        template = f.read()
    print(f"prompt template:\n{template}")
    return template.format(
        shrink_percent=shrink_percent,
        original_word_count=original_word_count,
        target_word_count=target_word_count,
        input_text=input_text.strip()
    )


def summarize_text(input_text: str, shrink_percent: int) -> str:
    original_word_count = count_words(input_text)
    print(f"Original text length: {original_word_count} words")
    prompt = build_prompt(input_text, original_word_count, shrink_percent)

    from call_api import chat_with_model
    response = chat_with_model(prompt, model="gpt-4o-mini")
    return response.strip()


#  Example usage of biuld_prompt
text = open("texts/samples/shortening_test.txt", "r", encoding="utf-8").read()
shrink_percent = 90  # Example shrink percentage
response = summarize_text(text, shrink_percent)

# Save the prompt to a new file
prompt_address = "texts/samples/shortening_test_prompt.txt"
with open(prompt_address, "w", encoding="utf-8") as f:
    f.write(response)

actual_shrink_percent = round((1 - count_words(response) / count_words(text)) * 100)
print(f"Actual shrink percentage: {actual_shrink_percent}%")
output_address = f"texts/samples/shortening_test_shrinked_{shrink_percent}_actual_{actual_shrink_percent}.txt"
with open(output_address, "w", encoding="utf-8") as f:
    f.write(response)


