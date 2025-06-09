import numpy as np
from sentence_transformers import CrossEncoder
import torch.nn.functional as F
import torch

def detecting_contradiction(teacher_units, student_unit):
    model = CrossEncoder('cross-encoder/nli-deberta-v3-base', num_labels=3)

    # קבלת הלוגיטים (שלושה ערכים)
    logits = model.predict([(teacher_units, student_unit)], convert_to_numpy=True)

    # הפעלת softmax כדי לקבל סבירויות
    probs = F.softmax(torch.tensor(logits[0]), dim=0).numpy()

    labels = ['contradiction', 'neutral', 'entailment']
    for label, prob in zip(labels, probs):
        print(f"{label}: {prob:.3f}")

    predicted_label = labels[np.argmax(probs)]
    # print(f"\The nli is: {predicted_label} (score = {probs.max():.3f})")
    return predicted_label, probs.max()

if __name__ == "__main__":
    premise = "Although the committee acknowledged the environmental concerns raised by the residents, they ultimately approved the construction of the new industrial facility."
    hypothesis = "I am sweet."
    detecting_contradiction(premise, hypothesis)
