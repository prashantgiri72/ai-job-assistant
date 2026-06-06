 
# utils/resume_parser.py

import fitz  # this is PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    """
    Reads a PDF file and extracts all text from it.
    pdf_path → path to your PDF file
    """
    text = ""

    # Open the PDF
    doc = fitz.open(pdf_path)

    # Loop through every page and extract text
    for page in doc:
        text += page.get_text()

    doc.close()
    return text


def clean_text(text):
    """
    Cleans the extracted text:
    - Removes extra whitespace
    - Removes extra blank lines
    - Converts to lowercase
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing spaces
    text = text.strip()

    # Convert to lowercase
    text = text.lower()

    return text


def parse_resume(pdf_path):
    """
    Main function — call this to get clean text from any PDF resume.
    Returns clean text as a string.
    """
    raw_text = extract_text_from_pdf(pdf_path)
    clean = clean_text(raw_text)
    return clean


# ---- TEST IT ----
if __name__ == "__main__":
    path = "data/resume.pdf"
    result = parse_resume(path)

    print("✅ Resume parsed successfully!")
    print(f"📄 Total characters extracted: {len(result)}")
    print("\n--- First 500 characters of your resume ---\n")
    print(result[:500])