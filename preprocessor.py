from story_list import stories
import os

def extract_gutenberg_text(file_path):
    start_pattern = "*** START OF THE PROJECT GUTENBERG EBOOK"
    end_pattern = "*** END OF THE PROJECT GUTENBERG EBOOK"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx, end_idx = None, None

    for i, line in enumerate(lines):
        if start_pattern in line:
            start_idx = i + 1  # exclude the start marker line
        elif end_pattern in line:
            end_idx = i        # exclude the end marker line
            break

    if start_idx is not None and end_idx is not None:
        return ''.join(lines[start_idx:end_idx])
    elif start_idx is not None:
        return ''.join(lines[start_idx:])
    elif end_idx is not None:
        return ''.join(lines[:end_idx])
    else:
        return ''.join(lines)



if __name__ == "__main__":
    # Process each file in the stories list
    for story_name in stories:
        story_path = f"texts/la_comédie_humaine_(balzac)/original/{story_name}.txt"  # Assuming the files are named with .txt extension
        cleaned_text = extract_gutenberg_text(story_path)

        # Optional: Save cleaned content to a new file
        # For example, write to `filename_cleaned.txt` in the same directory
        output_story_path = story_path.replace(".txt", "_cleaned.txt")
        output_story_path = output_story_path.replace("original", "preprocessed")

        with open(output_story_path, 'w', encoding='utf-8') as out_file:
            out_file.write(cleaned_text)

        print(f"Cleaned file written to: {output_story_path}")
