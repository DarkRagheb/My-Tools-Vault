import csv
from pathlib import Path
from typing import Union


NLP_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = NLP_DIRECTORY / "website_classification.csv"
DEFAULT_OUTPUT_DIRECTORY = NLP_DIRECTORY / "training_data"


def write_data(
    csv_path: Union[str, Path] = DEFAULT_CSV_PATH,
    output_directory: Union[str, Path] = DEFAULT_OUTPUT_DIRECTORY,
) -> None:
    """
    Write CSV rows to a scikit-learn load_files-compatible directory tree.

    dataset source: https://www.kaggle.com/hetulmehta/website-classification

    e.g.
    container_folder/
            category_1_folder/
                    file_1.txt file_2.txt file_3.txt ... file_42.txt
            category_2_folder/
                    file_43.txt file_44.txt ...
    """
    output_path = Path(output_directory)
    with Path(csv_path).open(newline="", encoding="utf-8", errors="replace") as csvfile:
        website_reader = csv.DictReader(csvfile)
        for row in website_reader:
            row_id = (row.get("id") or "").strip()
            content = row.get("cleaned_text") or ""
            category = (row.get("category") or "").strip().replace("/", "+")
            if not row_id or not content or not category:
                continue

            category_directory = output_path / category
            category_directory.mkdir(parents=True, exist_ok=True)
            (category_directory / f"{row_id}.txt").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    write_data()
