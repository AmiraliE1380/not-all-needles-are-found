from constant_vals import *
from counter import count_tokens

import math
import random
from typing import Dict, List


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


def inject_distributed_facts(facts: List[str], story: str, locations: List[float]) -> str:
    split_parts = story.split('\n\n')
    full_story = ''.join(split_parts)
    entire_story_token_count = count_tokens(full_story)

    print(f'len(split_parts) = {len(split_parts)}')
    story_with_fact = ""
    for part in split_parts:
        story_with_fact += part + '\n'
        # print(f'len(story_with_fact) = {len(story_with_fact)}')
        if len(facts) > 0 and count_tokens(story_with_fact) >= entire_story_token_count * locations[0]:
            # Inject the fact at this point
            while True:
                fact = facts[0]
                location = locations[0]
                facts = facts[1:]
                locations = locations[1:]
                story_with_fact += fact + '\n'
                print(f'len(story_with_fact) = {len(story_with_fact)}')
                print(location)
                if len(facts) == 0 or abs(locations[0] - location) > 0.0001:    # if the consecutive facts don't have same location
                    print('breaking')
                    break

    # print(f'story_with_fact = \n{story_with_fact}\n\n')
    return story_with_fact


# --------------------------------------------------------------------------- #
#  Location distributions
# --------------------------------------------------------------------------- #

# All possible injection locations
LOCATION_GRID: List[float] = [i * 0.05 for i in range(20)]  # 0.00 .. 0.95


def _normalize(weights: List[float]) -> List[float]:
    total = sum(weights)
    if total == 0:
        raise ValueError("Sum of weights is zero.")
    return [w / total for w in weights]


# Uniform
_uniform_weights = _normalize([1.0] * len(LOCATION_GRID))

# Normal (Gaussian) centered in the middle
_normal_mean = 0.5
_normal_std = 0.15
_normal_weights = _normalize([
    math.exp(-0.5 * ((x - _normal_mean) / _normal_std) ** 2)
    for x in LOCATION_GRID
])

# Exponential (decaying from left to right)
_exp_lambda = 4.0
_exponential_weights = _normalize([
    math.exp(-_exp_lambda * x) for x in LOCATION_GRID
])

# "Flipped" Exponential (increasing from left to right)
_exponential_flipped_weights = list(reversed(_exponential_weights))

# Bimodal (Gaussian mixture)
_bimodal_mu1 = 0.3
_bimodal_mu2 = 0.7
_bimodal_sigma = 0.08
_bimodal_weights = _normalize([
    math.exp(-0.5 * ((x - _bimodal_mu1) / _bimodal_sigma) ** 2)
    + math.exp(-0.5 * ((x - _bimodal_mu2) / _bimodal_sigma) ** 2)
    for x in LOCATION_GRID
])

# Arcsine on [0, 1] (peaks at both ends)
_eps = 1e-3
_arcsine_weights = _normalize([
    1.0 / math.sqrt(max(x, _eps) * max(1.0 - x, _eps))
    for x in LOCATION_GRID
])

# Lorentzian (Cauchy) centered in the middle
_cauchy_x0 = 0.5
_cauchy_gamma = 0.07
_cauchy_weights = _normalize([
    1.0 / (1.0 + ((x - _cauchy_x0) / _cauchy_gamma) ** 2)
    for x in LOCATION_GRID
])

# Rayleigh (peak toward the left side)
_rayleigh_sigma = 0.25
_rayleigh_weights = _normalize([
    (x / (_rayleigh_sigma ** 2)) * math.exp(-x * x / (2.0 * _rayleigh_sigma ** 2))
    for x in LOCATION_GRID
])

# "Flipped" Rayleigh (peak toward the right side)
_rayleigh_flipped_weights = list(reversed(_rayleigh_weights))


DISTRIBUTION_WEIGHTS: Dict[str, List[float]] = {
    # From first row
    "uniform": _uniform_weights,
    "normal": _normal_weights,
    "exponential": _exponential_weights,

    # Second row
    "exponential_flipped": _exponential_flipped_weights,
    "bimodal": _bimodal_weights,
    "bimodal_gaussian_mixture": _bimodal_weights,
    "arcsine": _arcsine_weights,

    # Third row
    "lorentzian": _cauchy_weights,
    "cauchy": _cauchy_weights,  # alias
    "rayleigh": _rayleigh_weights,
    "rayleigh_flipped": _rayleigh_flipped_weights,
}


def sample_location(distribution: str = "uniform", rng: random.Random = None) -> float:
    """
    Sample a location from LOCATION_GRID according to the given distribution.
    """
    if rng is None:
        rng = random

    try:
        weights = DISTRIBUTION_WEIGHTS[distribution]
    except KeyError:
        raise ValueError(f"Unknown distribution: {distribution!r}")

    # random.choices supports weighted sampling
    return rng.choices(LOCATION_GRID, weights=weights, k=1)[0]


if __name__ == "__main__":
    ######################## testing ############################
    
    # distributions
    dists = ["uniform", "normal", "exponential", "exponential_flipped",
             "bimodal_gaussian_mixture", "arcsine", "lorentzian",
             "rayleigh", "rayleigh_flipped"]
    # distribution = "uniform"  # change to "normal", "bimodal", "rayleigh", etc.
    # location = sample_location(distribution)

    # fact, story come from elsewhere
    # modified_story = inject_fact(fact, story, location)

    dist_facts_addr = "prompts/facts/distributed_facts.txt"
    with open(dist_facts_addr, 'r') as file:
        facts = file.read().split('\n\n')
    # print(f"facts = \n{facts}\n")
    print(len(facts))
    
    # locations = [sample_location(dists[1]) for _ in range(len(facts))]
    # locations.sort()
    # print(f"locations = \n{locations}\n")
    # print(len(locations))

    model = "gpt-5-mini"  # default model to use for chat_with_model
    max_context_length = 272 # number of thousands of tokens
    
    story_addr = f"texts/la_comédie_humaine_(balzac)/contracted/gpt/la_comédie_humaine_{max_context_length}k_expected_100%.txt"
    with open(story_addr, 'r', encoding='utf-8') as file:
        story = file.read()
    
    output_dir = "texts/la_comédie_humaine_(balzac)/contracted/distributed"

    for dist in dists:
        locations = [sample_location(dist) for _ in range(len(facts))]
        locations.sort()
        print(f"locations for {dist} = \n{locations}\n")
        
        modified_story = inject_distributed_facts(facts, story, locations)
        print(f"distribution: {dist}")
        print(f"locations: {locations}\n")
        
        output_addr = output_dir + f"/la_comédie_humaine_{max_context_length}k_distributed_{dist}.txt"
        with open(output_addr, 'w', encoding='utf-8') as file:
            file.write(modified_story)
        


    
