

RED = ["#f9f9f9", "#f2c9c9", "#ee9a9a", "#e55e5e", "#cc2929", "#640000"]
GREEN = ["#f9f9f9", "#c9f2c9", "#9aee9a", "#5ee55e", "#29cc29", "#006400"]
BLUE = ["#f9f9f9", "#c9d7f2", "#9abeee", "#5e8ee5", "#295ccc", "#000964"]
ORANGE = ["#f9f9f9", "#f2e0c9", "#eed09a", "#e5b05e", "#cc8a29", "#643900"]

model = "gpt-4o-mini"  # Default model name, can be overridden
def plot_grades(grades, save_path="heatmaps/heatmap.png", color_scheme=RED, color_scheme_name="red", title="Total Grades Heat-map"):
    """
    Render a numeric matrix (0–100) as a heat-map and save it to *save_path*.
    Each cell shows the value as a percentage with one decimal (e.g. 91.0%).
    The X axis is labeled "Context Length" and varies from 10% to 100%.
    The Y axis is labeled "Fact Depth" and varies from 10% to 100%.
    The X axis is stretched to be twice the size of the Y axis.
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.colors import LinearSegmentedColormap

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # --- colour map: white → deep red -----------------------------------------
    cmap = LinearSegmentedColormap.from_list(
        f"white_to_{color_scheme_name}",
        color_scheme,
        N=256,
    )

    # --- build string matrix like "91.0%" -------------------------------------
    annot_strings = np.vectorize(lambda x: f"{x:.1f}%")(grades)

    # --- X axis ticks: 10% to 100% --------------------------------------------
    num_cols = len(grades[0])
    x_labels = [f"{int(10 + (i * 90 / (num_cols - 1)))}%" for i in range(num_cols)] if num_cols > 1 else ["100%"]

    # --- Y axis ticks: 10% to 100% --------------------------------------------
    num_rows = len(grades)
    y_labels = [f"{int(10 + (i * 90 / (num_rows - 1)))}%" for i in range(num_rows)] if num_rows > 1 else ["100%"]

    # --- draw -----------------------------------------------------------------
    # Stretch x axis to be twice the size of y axis
    plt.figure(figsize=(2 * num_cols, num_rows), dpi=100)
    ax = sns.heatmap(
        grades,
        vmin=0,
        vmax=100,
        cmap=cmap,
        square=False,  # allow non-square aspect ratio
        linewidths=0.5,
        cbar_kws={"label": "Grade"},
        annot=annot_strings,   # use the strings with "%"
        fmt=""                 # disable seaborn's automatic formatting
    )
    ax.set_xlabel("Context Length")
    ax.set_xticks(np.arange(num_cols) + 0.5)
    ax.set_xticklabels(x_labels, rotation=0)

    ax.set_ylabel("Fact Depth")
    ax.set_yticks(np.arange(num_rows) + 0.5)
    ax.set_yticklabels(y_labels, rotation=0)

    plt.title(f'{title} for {model}')
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"Heat-map written to: {save_path}")


def retrieve_grades(grades, element_num):
    """
    Retrieve grades from a matrix of tuples and return as a matrix of numbers.
    """
    
    final_grades = []
    for row in grades:
        final_row = []
        for element in row:
            if isinstance(element, tuple):
                final_row.append(element[element_num])
            else:
                final_row.append(element)
        final_grades.append(final_row)

    return [list(row) for row in zip(*final_grades)]


if __name__ == "__main__":
    # Example usage
    grades_address = f"logs/grades_{model}.txt"
    save_path_total = f"heatmaps/{model}_total.png"
    save_path_direct = f"heatmaps/{model}_direct.png"
    save_path_inferential = f"heatmaps/{model}_inferential.png"
    save_path_hallucination = f"heatmaps/{model}_hallucination.png"

    with open(grades_address, 'r') as file:
        grades = eval(file.read())
    
    print(f"raw grades:\n {grades}")

    total_grades = retrieve_grades(grades, 0)
    print(f"Total grades: {total_grades}")
    direct_grades = retrieve_grades(grades, 1)
    print(f"Direct grades: {direct_grades}")
    inferential_grades = retrieve_grades(grades, 2)
    print(f"Inferential grades: {inferential_grades}")
    hallucination_grades = retrieve_grades(grades, 3)
    print(f"Hallucination grades: {hallucination_grades}")

    plot_grades(total_grades, save_path=save_path_total, color_scheme=BLUE, color_scheme_name="blue", title="Total Grades Heat-map")
    plot_grades(direct_grades, save_path=save_path_direct, color_scheme=BLUE, color_scheme_name="blue", title="Direct Facts Grades Heat-map")
    plot_grades(inferential_grades, save_path=save_path_inferential, color_scheme=BLUE, color_scheme_name="blue", title="Inferential Facts Grades Heat-map")
    plot_grades(hallucination_grades, save_path=save_path_hallucination, color_scheme=BLUE, color_scheme_name="blue", title="Hallucination Grades Heat-map")
    