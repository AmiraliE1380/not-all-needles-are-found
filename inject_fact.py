from constant_vals import *
from counter import count_tokens

import re


def inject_fact(fact, story, location):
    """
    Inject a fact into a story, ensuring the story remains coherent and within token limits.
    
    Args:
        fact (str): The fact to inject.
        story (str): The original story.
        location (float): The location in the story where the fact should be injected,
            represented as a percentage (0.0 to 1.0).
    
    Returns:
        str: The modified story with the fact injected.
    """

    # Split on either MIDDLE_OF_STORY or STORY_SEPERATOR
    # story = story.replace(STORY_SEPERATOR, '\n' + MIDDLE_OF_STORY + '\n')
    # split_parts = story.split(MIDDLE_OF_STORY)
    
    split_parts = story.split('\n')
    full_story = ''.join(split_parts)
    entire_story_token_count = count_tokens(full_story)

    story_with_fact = ""
    story_injected = False
    for part in split_parts:
        story_with_fact += part
        if not story_injected and count_tokens(story_with_fact) >= entire_story_token_count * location:
            # Inject the fact at this point
            story_with_fact += '\n\n' + fact + '\n\n'
            story_injected = True


    # print(f'story_with_fact = \n{story_with_fact}\n\n')
    return story_with_fact
