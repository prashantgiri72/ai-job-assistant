# test_setup.py
import sklearn
import nltk
import spacy
import fitz        # this is pymupdf
import streamlit
import anthropic

print("✅ scikit-learn:", sklearn.__version__)
print("✅ nltk:", nltk.__version__)
print("✅ spacy:", spacy.__version__)
print("✅ pymupdf (fitz):", fitz.__version__)
print("✅ streamlit:", streamlit.__version__)
print("✅ anthropic:", anthropic.__version__)
print("\n🎉 All libraries installed successfully!")