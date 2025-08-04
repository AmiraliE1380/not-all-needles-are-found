from shortening import *
from combiner import STORY_SEPERATOR

GPT_4O_MINI_CONTEXT_LENGTH = 128000  # Maximum context length for GPT-4o-mini in tokens
GPT_4O_MINI_CONTEXT_LENGTH_WORDS = 80000  # Conservative max context length for GPT-4o-mini in words
MIDDLE_OF_STORY = (
"\n################################################\n"
"\n############# MIDDLE OF THE STORY. #############\n"
"\n################################################\n"
)



input_story_addr = "texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_20000000.txt"
init_length_tokens = 2000000  # Target length for the final story
final_length_tokens = 128000  # Target length for the final story
shrinking_percent = shrink_percent(init_length_tokens, final_length_tokens)  # Target length for the final story
output_story_addr = "texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_20000000.txt"

# split the input text into stories and contract each story individually
print(f"Shrink percent: {shrinking_percent}%")
input_text = open(input_story_addr, "r", encoding="utf-8").read()
input_stories = input_text.split(STORY_SEPERATOR)
print(f"Number of stories in input: {len(input_stories)}")


output_story = ""
for i, story in enumerate(input_stories):
    contracted_story = contract_story(story, shrinking_percent)
    print(f"Story {i + 1} contracted: {len(contracted_story)} tokens")

    # Save each contracted story to a temporary file to avoid api issues
    temp_output_address = f"texts/la_comédie_humaine_(balzac)/contracted/temp/shrinked_{shrinking_percent}_story_{i + 1}.txt"
    with open(temp_output_address, "w", encoding="utf-8") as f:
        f.write(contracted_story)

    output_story += contracted_story + STORY_SEPERATOR


actual_output_length = count_words(output_story)
print(f"Total output length: {actual_output_length} tokens")

# save final output story
output_story_addr = f"texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_expected_{final_length_tokens}_words_{actual_output_length}.txt"

with open(output_story_addr, "w", encoding="utf-8") as f:
    f.write(output_story)   




def contract_story(story: str, shrink_percent: int) -> str:
    """
    Contracts a single story by a given shrink percentage.
    """
    if count_words(story) > GPT_4O_MINI_CONTEXT_LENGTH_WORDS:
        story_pieces = story.split(MIDDLE_OF_STORY)
        full_contracted_story = ""
        for piece in story_pieces:
            full_contracted_story += summarize_text(piece, shrink_percent) + MIDDLE_OF_STORY
        return full_contracted_story.strip()
    
    return summarize_text(story, shrink_percent)