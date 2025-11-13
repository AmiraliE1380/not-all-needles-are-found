from constant_vals import *
from counter import count_tokens


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


import math
import random
from typing import Dict, List

# All possible injection locations
LOCATION_GRID: List[float] = [i * 0.05 for i in range(20)]  # 0.00 .. 0.95


def _normalize(weights: List[float]) -> List[float]:
    total = sum(weights)
    if total == 0:
        raise ValueError("Sum of weights is zero.")
    return [w / total for w in weights]


# Precompute weights for each distribution over LOCATION_GRID
_uniform_weights = _normalize([1.0] * len(LOCATION_GRID))

_normal_mean = 0.5
_normal_std = 0.15
_normal_weights = _normalize([
    math.exp(-0.5 * ((x - _normal_mean) / _normal_std) ** 2)
    for x in LOCATION_GRID
])

DISTRIBUTION_WEIGHTS: Dict[str, List[float]] = {
    "uniform": _uniform_weights,
    "normal": _normal_weights,
    # later: "front_loaded": [...], "back_loaded": [...], etc.
}


def sample_location(distribution: str = "uniform", rng: random.Random = None) -> float:
    if rng is None:
        rng = random

    try:
        weights = DISTRIBUTION_WEIGHTS[distribution]
    except KeyError:
        raise ValueError(f"Unknown distribution: {distribution!r}")

    # random.choices supports weighted sampling
    return rng.choices(LOCATION_GRID, weights=weights, k=1)[0]


if __name__ == "__main__":
    distribution = "uniform"  # or "uniform", or arg/flag
    location = sample_location(distribution)
    
    for _ in range(40):
        loc = sample_location(distribution)
        print(f"Sampled location: {loc}")

    # fact, story come from elsewhere
    # modified_story = inject_fact(fact, story, location)
