"""
Summarize the entire series to ~800 words or ~1000 tokens using the GPT-4O Mini model.
"""

from counter import count_tokens
from call_api import chat_with_model

MIDDLE_OF_STORY = (
"\n################################################"
"\n############# MIDDLE OF THE STORY. #############"
"\n################################################\n"
)

input_story_addr = "texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_10%_actual_12451.txt"

# Read the input story
with open(input_story_addr, "r", encoding="utf-8") as file:
    input_story = file.read()

# Replace story delimiter with newline
input_story = input_story.replace(MIDDLE_OF_STORY, "\n")

# Read the summarization prompt template
with open("prompts/summarize.txt", "r", encoding="utf-8") as file:
    prompt_template = file.read()

# Insert the story into the prompt
prompt = prompt_template.replace("{text}", input_story)

# Call the model to summarize
output_story = chat_with_model(prompt, model="gpt-5-mini")

# Save the output with updated token count
output_story_addr = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_expected_1000_actual_{count_tokens(output_story)}.txt"

with open(output_story_addr, "w", encoding="utf-8") as file:
    file.write(output_story)

print(f"Summarized story saved to {output_story_addr}")