mov = [
    '11,"American President, The (1995)",Comedy|Drama|Romance',
    "6,Heat (1995),Action|Crime|Thriller",
    "30,Shanghai Triad (Yao a yao yao dao waipo qiao) (1995),Crime|Drama",
]


def to_list(line):
    in_quotes = False
    part = ""
    for symbol in line:

        if symbol == '"':
            in_quotes = not in_quotes

        if symbol == ",":
            if in_quotes:
                part += symbol
            else:
                part = ""
        else:
            part += symbol
    genres = part
    return genres


def date(title):
    for part in title.split("("):
        if ")" in part:
            if len(part[: part.find(")")]) < 5:
                return part[: part.find(")")]


for m in mov:
    print(to_list(m).split('|'))
