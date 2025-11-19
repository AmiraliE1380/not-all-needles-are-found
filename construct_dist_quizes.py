from inject_fact import sample_location


def inject_locations(story:str, locations: list[float]) -> str:
    return story


if __name__ == "__main__":
    locations = [sample_location(i) for i in range(10)].sort()

    
