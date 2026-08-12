import importlib
import os
import sys


def import_real_nlp_module():
    """Import the real NLP module instead of the lightweight test stub."""
    sys.modules.pop("torbot.modules.nlp.main", None)
    return importlib.import_module("torbot.modules.nlp.main")


def write_fixture_csv(path):
    path.write_text(
        "\n".join(
            [
                "id,website,cleaned_text,category",
                "1,https://sports.test,basketball team score playoff coach,Sports",
                "2,https://sports2.test,football league match tournament goal,Sports",
                "3,https://biz.test,revenue company shareholder market,Business",
                "4,https://biz2.test,corporate earnings sales customer,Business",
            ]
        ),
        encoding="utf-8",
    )


def test_extract_text_normalizes_html() -> None:
    nlp = import_real_nlp_module()

    assert nlp.extract_text("<html><h1>Hello</h1><p>World</p></html>") == "Hello World"


def test_load_training_rows_uses_csv_without_training_directory(tmp_path) -> None:
    nlp = import_real_nlp_module()
    csv_path = tmp_path / "website_classification.csv"
    write_fixture_csv(csv_path)

    texts, labels = nlp.load_training_rows(csv_path)

    assert len(texts) == 4
    assert sorted(set(labels)) == ["Business", "Sports"]
    assert not (tmp_path / "training_data").exists()


def test_build_classifier_returns_category_and_confidence(tmp_path) -> None:
    nlp = import_real_nlp_module()
    csv_path = tmp_path / "website_classification.csv"
    write_fixture_csv(csv_path)

    classifier = nlp.build_classifier(csv_path)
    text = "basketball team wins playoff tournament"
    prediction = classifier.predict([text])[0]
    confidence = nlp._prediction_score(classifier, text)

    assert prediction == "Sports"
    assert 0.0 <= confidence <= 1.0


def test_classify_empty_html_returns_unknown() -> None:
    nlp = import_real_nlp_module()

    assert nlp.classify("") == ["unknown", 0.0]


def test_gather_data_writes_training_files_without_changing_cwd(tmp_path) -> None:
    from torbot.modules.nlp.gather_data import write_data

    csv_path = tmp_path / "website_classification.csv"
    output_path = tmp_path / "training_data"
    write_fixture_csv(csv_path)
    before = os.getcwd()

    write_data(csv_path=csv_path, output_directory=output_path)

    assert os.getcwd() == before
    assert (output_path / "Sports" / "1.txt").read_text(encoding="utf-8")
    assert (output_path / "Business" / "3.txt").read_text(encoding="utf-8")
