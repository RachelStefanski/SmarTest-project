import spacy

nlp = spacy.load("en_core_web_sm")

def get_numeric_value(token):
    if token.like_num:
        try:
            return int(token.text)
        except ValueError:
            return 1
    return 1

def extract_demands_by_parts(text):
    doc = nlp(text)
    demands = []
    seen = set()

    for token in doc:
        # מחפשים שמות עצם שיש להם מספר (nummod) או שמספר מקושר אליהם ישיר
        num_token = None
        for child in token.children:
            if child.dep_ == "nummod":
                num_token = child
                break
        if num_token and token.pos_ == "NOUN":
            num = get_numeric_value(num_token)

            # אוספים תארים שמחוברים ישירות לשם העצם (amod)
            adjs = [child for child in token.children if child.dep_ == "amod" and child.pos_ == "ADJ"]

            # מוסיפים תארים שמחוברים ב-conj ל-amod (כמו במבנה 'political and economic')
            # נבדוק תארים שמחוברים בקונקטור לתארים הראשוניים
            extra_adjs = []
            for adj in adjs:
                for conj in adj.conjuncts:
                    if conj.pos_ == "ADJ":
                        extra_adjs.append(conj)
            all_adjs = adjs + extra_adjs

            # אם אין תארים, פשוט שם העצם
            if not all_adjs:
                category = token.text
                if category not in seen:
                    demands.append({"category": category, "num": num})
                    seen.add(category)
            else:
                # לכל תואר יוצרים קטגוריה נפרדת עם אותו מספר
                for adj in all_adjs:
                    category = f"{adj.text} {token.text}"
                    if category not in seen:
                        demands.append({"category": category, "num": num})
                        seen.add(category)

    return demands


if __name__ == "__main__":
    question = "Give 2 reasons people supported fascist leaders and 2 reasons they opposed them. Explain how each reason contributed to the rise of fascism."
    results = extract_demands_by_parts(question)
    print("🔹 דרישות שזוהו:")
    for item in results:
        print(f" - category: {item['category']}, num: {item['num']}")

    # הצגת עצי תלות לטובת דיבוג (אופציונלי)
    doc = nlp(question)
    for token in doc:
        print(f"{token.text:<12} {token.dep_:<10} --> {token.head.text:<12} ({token.head.pos_})")
