import pandas as pd
import PyPDF2
import pdf2text
import spacy
import nltk
import matplotlib.pyplot as plt

class DataProcessing:
    def __init__(self):
        nltk.download('punkt')
        self.nlp = spacy.load('en_core_web_sm')

    def parse_csv(self, file_path):
        return pd.read_csv(file_path)

    def parse_excel(self, file_path):
        return pd.read_excel(file_path)

    def extract_pdf_text(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            text = ''
            for page_num in range(reader.numPages):
                text += reader.getPage(page_num).extract_text()
        return text

    def basic_nlp(self, text):
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def visualize_data(self, data, title='Data Visualization'):
        plt.figure(figsize=(10, 5))
        plt.plot(data)
        plt.title(title)
        plt.show()
