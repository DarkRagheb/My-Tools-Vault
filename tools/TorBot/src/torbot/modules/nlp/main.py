"""
Website text classification helpers.

The classifier is trained lazily from the packaged CSV and cached for the
process lifetime. That keeps LinkTree classification cheap after the first
call and avoids writing generated training files into the installed package.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline


NLP_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_DATASET_PATH = NLP_DIRECTORY / "website_classification.csv"


def extract_text(html: str) -> str:
    """Extract normalized visible text from an HTML document."""
    soup = BeautifulSoup(html or "", features="html.parser")
    return soup.get_text(" ", strip=True)


def load_training_rows(
    csv_path: Union[str, Path] = DEFAULT_DATASET_PATH,
) -> Tuple[List[str], List[str]]:
    """Load training text and labels from the website classification CSV."""
    path = Path(csv_path)
    texts: list[str] = []
    labels: list[str] = []

    with path.open(newline="", encoding="utf-8", errors="replace") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            text = (row.get("cleaned_text") or "").strip()
            category = (row.get("category") or "").strip()
            if text and category:
                texts.append(text)
                labels.append(category)

    if not texts:
        raise ValueError(f"no training rows found in {path}")

    if len(set(labels)) < 2:
        raise ValueError(f"at least two categories are required in {path}")

    return texts, labels


def build_classifier(csv_path: Union[str, Path] = DEFAULT_DATASET_PATH) -> Pipeline:
    """Train a text classifier from the supplied dataset CSV."""
    texts, labels = load_training_rows(csv_path)
    classifier = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    max_features=50000,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                SGDClassifier(
                    class_weight="balanced",
                    loss="modified_huber",
                    max_iter=1000,
                    random_state=42,
                    tol=1e-3,
                ),
            ),
        ]
    )
    classifier.fit(texts, labels)
    return classifier


@lru_cache(maxsize=4)
def get_classifier(csv_path: Union[str, Path] = DEFAULT_DATASET_PATH) -> Pipeline:
    """Return a cached classifier for the requested dataset."""
    return build_classifier(Path(csv_path).resolve())


def _prediction_score(classifier: Pipeline, text: str) -> float:
    """Return a best-effort confidence score for a single prediction."""
    if hasattr(classifier, "predict_proba"):
        probabilities = classifier.predict_proba([text])[0]
        return float(np.max(probabilities))

    if hasattr(classifier, "decision_function"):
        scores = np.asarray(classifier.decision_function([text]))
        return float(np.max(scores))

    return 0.0


def classify(data: str) -> List[Union[str, float]]:
    """
    Classify the supplied HTML and return [category, confidence].

    The confidence value is model confidence for the selected category, not a
    model-wide accuracy score.
    """
    text = extract_text(data)
    if not text:
        return ["unknown", 0.0]

    classifier = get_classifier()
    prediction = classifier.predict([text])[0]
    confidence = _prediction_score(classifier, text)
    return [str(prediction), confidence]
