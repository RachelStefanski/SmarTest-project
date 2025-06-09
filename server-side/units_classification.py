from sentence_transformers import CrossEncoder
import numpy as np

def match_units_to_categories(units, requirements, model):
    categorized_units = []

    for text in units:
        pairs = [(text, req.category) for req in requirements]
        print(pairs)
        scores = model.predict(pairs)

        # softmax על הסקור
        exp_scores = np.exp(scores - np.max(scores))
        probabilities = exp_scores / exp_scores.sum()

        best_idx = np.argmax(probabilities)
        best_cat = requirements[best_idx].category  # ← כאן התיקון
        best_prob = probabilities[best_idx]

        categorized_units.append((text, best_cat))
        print(f"\nSentence: '{text}'\n→ Predicted category: '{best_cat}' (probability: {best_prob:.4f})")

    return categorized_units


if __name__ == "__main__":
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    categories = [
        "Political reasons",
        "Security reasons",
        "Economic reasons",
    ]

    units = [
        "The government passed a new law to strengthen the economy.",
        "The military increased its presence near the border.",
        "Elections will be held next month.",
        "Prices of goods have risen dramatically.",
        "A new security protocol was implemented after the attack.",
        "People protested against the political corruption."
    ]

    categorized, stats = match_units_to_categories(units, categories, model)

    print("\nSummary:")
    for unit, cat in categorized:
        print(f"'{unit}' → {cat}")

    print("\nCategory counts:", stats)
