import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QFileDialog, QWidget, QListWidget, QProgressBar, QTextEdit
from pdfminer.high_level import extract_text
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dateutil.parser import parse
from elasticsearch import Elasticsearch
from haystack.utils import launch_es, print_questions
from haystack.nodes import QuestionGenerator, BM25Retriever, FARMReader
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.pipelines import (
    QuestionGenerationPipeline,
    RetrieverQuestionGenerationPipeline,
    QuestionAnswerGenerationPipeline,
)

class FileSelectWindow(QWidget):
    def __init__(self):
        super(FileSelectWindow, self).__init__()

        self.list_widget = QListWidget()
        self.file_paths = []

        select_button = QPushButton('PDFs auswählen')
        select_button.clicked.connect(self.on_select_clicked)

        continue_button = QPushButton('Weiter')
        continue_button.clicked.connect(self.on_continue_clicked)

        layout = QVBoxLayout()
        layout.addWidget(select_button)
        layout.addWidget(self.list_widget)
        layout.addWidget(continue_button)

        self.setLayout(layout)

    def on_select_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames(None, 'Open File', '', 'PDF Files (*.pdf)')
        for filename in filenames:
            self.list_widget.addItem(filename)
            self.file_paths.append(filename)

    def on_continue_clicked(self):
        self.close()
        self.new_window = TextEditWindow(self.file_paths)
        self.new_window.show()


class TextEditWindow(QWidget):
    def __init__(self, file_paths):
        super(TextEditWindow, self).__init__()
        
        self.file_paths = file_paths
        self.spinner = QProgressBar(self)
        self.spinner.setRange(0, 0)

        self.spinner.show()
        layout = QVBoxLayout()
        self.text_edits = []

        for path in self.file_paths:
            text_edit = QTextEdit(self)
            layout.addWidget(text_edit)
            self.text_edits.append(text_edit)

        next_button = QPushButton('Weiter')
        next_button.clicked.connect(self.next_step)
        layout.addWidget(next_button)

        self.setLayout(layout)

        self.extracted_texts = []
        self.filter_words = ['INNSBRUCK', 'Innsbruck', 'UNTERNEHMERISCHE', 'DIE', 'HOCHSCHULE', 'Austria', 'Universitätsstraße','®','M','CI', 'ANAGEM','ENT', 'CENTER','6020','/', 'www.mci.edu', 'office@mci.edu']
        self.nlp = spacy.load('en_core_web_sm')
        
        for path in file_paths:
            text  = extract_text(path)
            text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])

            clean = ""

            for line in text.splitlines():
                if (not self.is_valid_sentence(line)) or is_date(line):
                    continue
                doc = self.nlp(line)
                for token in doc:
                    if token.text not in self.filter_words and not token.like_url and not token.like_email:
                        clean = clean + token.text
                clean = clean + " "
            self.extracted_texts.append(clean)
        
        for (index, edit) in enumerate(self.text_edits):
            edit.setPlainText(self.extracted_texts[index])
        self.spinner.hide()
    
    def is_valid_sentence(self, text):
        doc = self.nlp(text)
        sentences = list(doc.sents)
        return text in [sent.text for sent in sentences]


    def next_step(self): 
        res = []
        for (index, edit) in enumerate(self.text_edits):
            res.append(edit.toPlainText())
        self.close()
        self.new_window = QuestionsWindow(res)
        self.new_window.show()


class QuestionsWindow(QWidget):
    def __init__(self, docs):
        super(QuestionsWindow, self).__init__()

        layout = QVBoxLayout()
        self.text_edits = []
        
        self.delete_all_documents()
        questions = generate_questions(docs)   
        print(questions)  
        text_edit = QTextEdit(self)
        text_edit.setPlainText("questions")
        layout.addWidget(text_edit)
        self.text_edits.append(text_edit)

        self.setLayout(layout)


    def delete_all_documents(self): 
        es = Elasticsearch(persistent=False)
        index_name = "document"

        query = {
            "query": {
                "match_all": {}
            }
        }
        es.delete_by_query(index=index_name, body=query)



def generate_questions(texts):

        docs = [{"content": text} for text in texts]
        
        document_store = ElasticsearchDocumentStore()
        document_store.write_documents(docs)

        # # # Initialize Question Generator
        question_generator = QuestionGenerator()
        question_generation_pipeline = QuestionGenerationPipeline(question_generator)

        results = []
        for idx, document in enumerate(document_store):

            print(f"\n * Generating questions for document {idx}: {document.content[:100]}...\n")
            result = question_generation_pipeline.run(documents=[document])
            for doc in result['documents']:
                for question in doc['generated_questions']:
                    results.append(question['question'])

        return results


def is_date(string, fuzzy=False):
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def main():
    app = QApplication([])

    window = FileSelectWindow()
    window.show()

    app.exec_()

if __name__ == '__main__':
    main()
