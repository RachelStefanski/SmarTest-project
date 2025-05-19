from wtpsplit import SaT
sat = SaT("sat-12l-sm")

def split_text(text_to_split):
    semantic_units = sat.split(text_to_split)
    return semantic_units
