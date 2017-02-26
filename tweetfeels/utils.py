from re import sub

def clean(text):
    text = text.lower()
    text = sub("[0-9]+", "number", text)
    text = sub("#", "", text)
    text = sub("\\n", "", text)
    text = text.replace('$', '@')
    text = sub("@[^\\s]+", "", text)
    text = sub("(http|https)://[^\\s]*", "", text)
    text = sub("[^\\s]+@[^\\s]+", "", text)
    text = sub('[^a-z A-Z]+', '', text)
    return text
