import json
import numpy as np
import faiss
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "few_shot_examples.json"

with open(_DATA_PATH, "r", encoding="utf-8") as f:
    _EXAMPLES = json.load(f)

_questions = [ex["question"] for ex in _EXAMPLES]

_vectorizer = TfidfVectorizer()
_tfidf_matrix = _vectorizer.fit_transform(_questions).toarray().astype("float32")

_dimension = _tfidf_matrix.shape[1]
_index = faiss.IndexFlatL2(_dimension)
_index.add(_tfidf_matrix)


def get_relevant_examples(question: str, k: int = 3):
    query_vec = _vectorizer.transform([question]).toarray().astype("float32")
    distances, indices = _index.search(query_vec, k)
    results = []
    for idx in indices[0]:
        if idx < len(_EXAMPLES):
            results.append(_EXAMPLES[idx])
    return results


def format_examples_for_prompt(examples: list) -> str:
    lines = []
    for ex in examples:
        lines.append(f"Câu hỏi: {ex['question']}\nSQL: {ex['sql']}")
    return "\n\n".join(lines)