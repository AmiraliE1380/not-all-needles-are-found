import os


STORY_SEPERATOR = ("\n\n################################################\n"
                        "######### THIS IS THE END OF A STORY. #########\n"
                        "################################################\n\n")


def combine_files(file_names, input_dir, output_file, output_dir):
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
    output_path = os.path.join(output_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for name in file_names:
            file_path = os.path.join(input_dir, f"{name}_cleaned.txt")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    outfile.write(STORY_SEPERATOR)  # Optional: separate files by newline
            else:
                print(f"Warning: {file_path} does not exist and will be skipped.")



if __name__ == "__main__":
    from story_list import stories

    input_directory = "texts/la_comédie_humaine_(balzac)/preprocessed"
    output_directory = "texts/la_comédie_humaine_(balzac)/all_combined"
    output_filename = "la_comédie_humaine_all.txt"

    combine_files(stories, input_directory, output_filename, output_directory)
    print(f"Combined {len(stories)} stories into {output_filename} in {output_directory}.")

    from counter import count_words_and_tokens
    count_words_and_tokens(f'{output_directory}/{output_filename}')