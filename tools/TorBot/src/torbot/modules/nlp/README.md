# Natural Language Processing Module

This module classifies crawled pages into broad website categories using the
packaged `website_classification.csv` dataset.

Runtime classification uses `classify(html)` from `main.py`. The classifier is
trained lazily from the CSV on first use and cached for the rest of the process,
so crawling multiple pages does not retrain the model for every page.

## Public API

```python
from torbot.modules.nlp.main import classify

category, confidence = classify("<html>...</html>")
```

`confidence` is the model's confidence for the selected category. It is not a
model-wide accuracy score.

## Optional training-data export

The crawler no longer needs a generated `training_data/` directory. If you need
one for experiments with `sklearn.datasets.load_files`, run:

```sh
python3 -m torbot.modules.nlp.gather_data
```

This creates an ignored `training_data/` directory beside the NLP module.
