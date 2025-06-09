import spacy
from word2number import w2n

nlp = spacy.load("en_core_web_trf")

class Requirement:
    def __init__(self, category, quantity=1, verb=None):
        self.category = category.strip()
        self.quantity = quantity or 1
        self.verb = verb

    def __repr__(self):
        return f"Requirement(category='{self.category}', quantity={self.quantity}, verb='{self.verb}')"

    def to_dict(self):
        return {
            'category': self.category,
            'quantity': self.quantity,
            'verb': self.verb
        }

    def from_dict(d):
        return Requirement(d['category'], d.get('quantity'), d.get('verb'))


def split_conjoined_phrases(text):
    import re
    # מפצל לפי פסיקים ו־"and", אבל שומר על ביטויים מורכבים
    return [s.strip() for s in re.split(r',|\band\b', text) if s.strip()]


def extract_quantity(text):
    try:
        return int(text)
    except:
        try:
            return w2n.word_to_num(text)
        except:
            return None


def clean_category(text):
    doc = nlp(text)
    return " ".join(tok.text for tok in doc if tok.pos_ not in {"DET", "PART", "INTJ", "CCONJ", "SCONJ"})


def get_requirement_source(sent):
    for tok in sent:
        if tok.pos_ == "VERB" and any(c.dep_ in {"dobj", "pobj", "attr", "xcomp", "ccomp", "obl", "nsubj"} for c in tok.children):
            return tok.text
    for tok in sent:
        if tok.tag_ in {"WDT", "WP", "WP$", "WRB"}:
            return tok.text
    return None


def extract_phrases_and_requirements(span_text, verb):
    reqs = []
    for phrase in split_conjoined_phrases(span_text):
        quantity = None
        for t in nlp(phrase):
            if t.like_num:
                quantity = extract_quantity(t.text)
                phrase = phrase.replace(t.text, "").strip()
                break
        if quantity is None:
            quantity = 1

        category = clean_category(phrase)
        if category:
            reqs.append(Requirement(category=category, quantity=quantity, verb=verb))
    return reqs


def extract_requirements(text):
    doc = nlp(text)
    all_reqs = []

    for sent in doc.sents:
        sent_reqs = []
        verbs = [tok for tok in sent if tok.pos_ == "VERB"]
        found = False

        for verb in verbs:
            for tok in sent:
                if tok.head == verb and tok.dep_ in {"dobj", "pobj", "attr", "xcomp", "ccomp", "obl", "nsubj", "conj"}:
                    subtree = sorted(list(tok.subtree), key=lambda t: t.i)
                    span_text = text[subtree[0].idx:subtree[-1].idx + len(subtree[-1])]
                    sent_reqs.extend(extract_phrases_and_requirements(span_text, verb.text))
                    found = True

        if not found:
            source = get_requirement_source(sent)
            for tok in sent:
                subtree = sorted(list(tok.subtree), key=lambda t: t.i)
                span_text = text[subtree[0].idx:subtree[-1].idx + len(subtree[-1])]
                sent_reqs.extend(extract_phrases_and_requirements(span_text, source))

        all_reqs.extend(sent_reqs)

    # סינון כפילויות ודרישות מוכללות
    filtered, seen = [], set()
    for req in all_reqs:
        key = (req.category.lower(), (req.verb or "").lower())
        if key in seen:
            continue
        if req.verb and req.verb.lower() in req.category.lower():
            continue
        if any(
            req.category.lower() in other.category.lower() and
            req.category.lower() != other.category.lower()
            for other in all_reqs
        ):
            continue
        seen.add(key)
        filtered.append(req)

    return filtered


# דוגמה לשימוש
if __name__ == "__main__":
    question = "Discuss how nationalism, militarism, and alliances contributed to the outbreak of World War I."
    for r in extract_requirements(question):
        print(r)
