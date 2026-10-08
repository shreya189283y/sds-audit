import pdfplumber

def read_pdf(path):
    #Return all the text in a PDF as one string.
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def is_scanned(text):
    #True if the PDF gave back too little text to be a real SDS.
    return len(text.strip()) < 200