import os
from constant_vals import STORY_SEPERATOR

def combine_files(file_names, output_file, output_dir):
    """
    Combines text files from input_dir with names in file_names (adding '.txt') 
    into a single file output_file in output_dir.

    Args:
        file_names (list of str): List of file base names (without extension).
        input_dir (str): Directory containing the input files.
        output_file (str): Name of the output file (should end with .txt).
        output_dir (str): Directory to save the combined file.
    """
    os.makedirs(output_dir, exist_ok=True)
    text = ""

    file_names.sort()  # Sort the file names to ensure consistent order

    for name in file_names:
        file_path = name
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as infile:
                text += infile.read()
                text += STORY_SEPERATOR  # Optional: separate files by newline
        else:
            print(f"Warning: {file_path} does not exist and will be skipped.")
    
    
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(text)



if __name__ == "__main__":
    # from constant_vals import stories

    input_directory = "texts/la_comédie_humaine_(balzac)/contracted/temp"
    output_directory = "texts/la_comédie_humaine_(balzac)/all_combined"
    output_filename = "combined_test.txt"

    shrink_precentage = 50

    input_files = os.listdir(input_directory)

    story_addresses = []
    for file in input_files:
        if file.startswith(f'shrinked_{shrink_precentage}_'):
            story_addresses.append(f'{input_directory}/{file}')

    combine_files(story_addresses, output_filename, output_directory)
    print(f"Combined {len(story_addresses)} stories into {output_filename} in {output_directory}.")

    from counter import count_words_and_tokens
    count_words_and_tokens(f'{output_directory}/{output_filename}')