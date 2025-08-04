from shortening import shrink_percent
from combiner import STORY_SEPERATOR


input_story_addr = "texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_20000000.txt"
init_length_tokens = 2000000  # Target length for the final story
final_length_tokens = 128000  # Target length for the final story
shrink_percent = shrink_percent(init_length_tokens, final_length_tokens)  # Target length for the final story
output_story_addr = "texts/la_comédie_humaine_(balzac)/contracted/la_comédie_humaine_20000000.txt"

print(f"Shrink percent: {shrink_percent}%")
input_text = open(input_story_addr, "r", encoding="utf-8").read()
input_stories = input_text.split(STORY_SEPERATOR)
print(f"Number of stories in input: {len(input_stories)}")