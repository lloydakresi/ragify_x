import pdfplumber as pp
corpus_path = "../corpus/d2l-en.pdf"

with pp.open(corpus_path) as f:
    for page in f.pages:
        print(page.extract_text())
