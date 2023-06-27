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
from lxml import etree
import random 
import string

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
        questions_string = '\n'.join(questions)

        text_edit = QTextEdit(self)
        text_edit.setPlainText(questions_string)
        layout.addWidget(text_edit)

        next_button = QPushButton('Fragen exportieren')
        next_button.clicked.connect(self.next_step)
        layout.addWidget(next_button)
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

    def next_step(self): 
        questions = self.text_edits[0].toPlainText().split('\n')
        
        # Define the qtimetadatafields
        qtimetadatafields = [
            ('AUTHORS', None),
            ('CREATOR', None),
            ('SHOW_CREATOR', 'True'),
            ('SCALENAME', 'STRONGLY_AGREE'),
            ('EDIT_AUTHORS', 'True'),
            ('EDIT_DESCRIPTION', 'True'),
            ('ATTACHMENT', None),
            ('DISPLAY_TEMPLATE', 'True'),
            ('START_DATE', None),
            ('END_DATE', None),
            ('RETRACT_DATE', None),
            ('CONSIDER_START_DATE', 'False'),
            ('CONSIDER_END_DATE', 'False'),
            ('CONSIDER_RETRACT_DATE', 'False'),
            ('EDIT_END_DATE', 'True'),
            ('EDIT_RETRACT_DATE', 'True'),
            ('ASSESSMENT_RELEASED_TO', 'Personal'),
            ('EDIT_PUBLISH_ANONYMOUS', 'True'),
            ('EDIT_AUTHENTICATED_USERS', 'True'),
            ('ALLOW_IP', None),
            ('CONSIDER_ALLOW_IP', 'False'),
            ('CONSIDER_USERID', 'False'),
            ('PASSWORD', None),
            ('EDIT_ALLOW_IP', 'True'),
            ('EDIT_USERID', 'True'),
            ('REQUIRE_LOCKED_BROWSER', 'False'),
            ('EXIT_PASSWARD', None),
            ('CONSIDER_DURATION', 'False'),
            ('AUTO_SUBMIT', 'True'),
            ('EDIT_DURATION', 'True'),
            ('EDIT_AUTO_SUBMIT', 'True'),
            ('NAVIGATION', 'RANDOM'),
            ('QUESTION_LAYOUT', 'I'),
            ('QUESTION_NUMBERING', 'CONTINUOUS'),
            ('EDIT_NAVIGATION', 'True'),
            ('EDIT_QUESTION_LAYOUT', 'True'),
            ('EDIT_QUESTION_NUMBERING', 'True'),
            ('MARK_FOR_REVIEW', 'False'),
            ('LATE_HANDLING', 'True'),
            ('MAX_ATTEMPTS', '9999'),
            ('EDIT_LATE_HANDLING', 'True'),
            ('EDIT_MAX_ATTEMPTS', 'True'),
            ('AUTO_SAVE', 'False'),
            ('EDIT_AUTO_SAVE', 'True'),
            ('EDIT_ASSESSFEEDBACK', 'True'),
            ('SUBMISSION_MESSAGE', etree.CDATA(''),),
            ('FINISH_URL', None),
            ('EDIT_FINISH_URL', 'True'),
            ('FEEDBACK_DELIVERY', 'NONE'),
            ('FEEDBACK_COMPONENT_OPTION', 'SELECT_COMPONENTS'),
            ('FEEDBACK_AUTHORING', 'QUESTION'),
            ('FEEDBACK_DELIVERY_DATE', None),
            ('FEEDBACK_DELIVERY_END_DATE', None),
            ('EDIT_FEEDBACK_DELIVERY', 'True'),
            ('EDIT_FEEDBACK_COMPONENTS', 'True'),
            ('FEEDBACK_SHOW_CORRECT_RESPONSE', 'False'),
            ('FEEDBACK_SHOW_STUDENT_SCORE', 'False'),
            ('FEEDBACK_SHOW_STUDENT_QUESTIONSCORE', 'False'),
            ('FEEDBACK_SHOW_ITEM_LEVEL', 'False'),
            ('FEEDBACK_SHOW_SELECTION_LEVEL', 'False'),
            ('FEEDBACK_SHOW_GRADER_COMMENT', 'False'),
            ('FEEDBACK_SHOW_STATS', 'False'),
            ('FEEDBACK_SHOW_QUESTION', 'True'),
            ('FEEDBACK_SHOW_RESPONSE', 'False'),
            ('ANONYMOUS_GRADING', 'False'),
            ('GRADE_SCORE', 'HIGHEST_SCORE'),
            ('GRADEBOOK_OPTIONS', 'NONE'),
            ('EDIT_GRADEBOOK_OPTIONS', 'True'),
            ('EDIT_ANONYMOUS_GRADING', 'True'),
            ('EDIT_GRADE_SCORE', 'True'),
            ('BGCOLOR', None),
            ('BGIMG', None),
            ('EDIT_BGCOLOR', 'True'),
            ('EDIT_BGIMG', 'True'),
            ('EDIT_ASSESSMENT_METADATA', 'True'),
            ('EDIT_COLLECT_SECTION_METADATA', 'True'),
            ('EDIT_COLLECT_ITEM_METADATA', 'True'),
            ('ASSESSMENT_KEYWORDS', None),
            ('ASSESSMENT_OBJECTIVES', None),
            ('ASSESSMENT_RUBRICS', None),
            ('COLLECT_SECTION_METADATA', 'False'),
            ('COLLECT_ITEM_METADATA', None),
            ('LAST_MODIFIED_ON', None),
            ('LAST_MODIFIED_BY', None),
            ('templateInfo_isInstructorEditable', 'true'),
            ('assessmentAuthor_isInstructorEditable', 'true'),
            ('assessmentCreator_isInstructorEditable', None),
            ('description_isInstructorEditable', 'true'),
            ('dueDate_isInstructorEditable', 'true'),
            ('retractDate_isInstructorEditable', 'true'),
            ('anonymousRelease_isInstructorEditable', 'true'),
            ('authenticatedRelease_isInstructorEditable', 'true'),
            ('ipAccessType_isInstructorEditable', 'true'),
            ('passwordRequired_isInstructorEditable', 'true'),
            ('lockedBrowser_isInstructorEditable', 'true'),
            ('timedAssessment_isInstructorEditable', 'true'),
            ('timedAssessmentAutoSubmit_isInstructorEditable', 'true'),
            ('itemAccessType_isInstructorEditable', 'true'),
            ('displayChunking_isInstructorEditable', 'true'),
            ('displayNumbering_isInstructorEditable', 'true'),
            ('displayScores_isInstructorEditable', 'true'),
            ('submissionModel_isInstructorEditable', 'true'),
            ('lateHandling_isInstructorEditable', 'true'),
            ('instructorNotification_isInstructorEditable', 'True'),
            ('automaticSubmission_isInstructorEditable', 'true'),
            ('autoSave_isInstructorEditable', None),
            ('submissionMessage_isInstructorEditable', 'true'),
            ('finalPageURL_isInstructorEditable', 'true'),
            ('feedbackType_isInstructorEditable', 'true'),
            ('feedbackComponents_isInstructorEditable', 'true'),
            ('testeeIdentity_isInstructorEditable', 'true'),
            ('toGradebook_isInstructorEditable', 'true'),
            ('recordedScore_isInstructorEditable', 'true'),
            ('bgColor_isInstructorEditable', 'true'),
            ('bgImage_isInstructorEditable', 'true'),
            ('metadataAssess_isInstructorEditable', 'true'),
            ('metadataParts_isInstructorEditable', None),
            ('metadataQuestions_isInstructorEditable', 'true'),
            ('honorpledge_isInstructorEditable', 'true')
        ]

        # Create the root element
        root = etree.Element('questestinterop')

        # Create the assessment element
        assessment = etree.SubElement(root, 'assessment', ident='7739', title='TestQuiz')

        # Add the rest of the elements under assessment
        qticomment = etree.SubElement(assessment, 'qticomment')
        duration = etree.SubElement(assessment, 'duration')
        qtimetadata = etree.SubElement(assessment, 'qtimetadata')

        # Add the qtimetadatafields to the qtimetadata element
        for label, entry in qtimetadatafields:
            qtimetadatafield = etree.SubElement(qtimetadata, 'qtimetadatafield')
            fieldlabel = etree.SubElement(qtimetadatafield, 'fieldlabel')
            fieldlabel.text = label
            fieldentry = etree.SubElement(qtimetadatafield, 'fieldentry')
            if entry is not None:
                # Check if the entry is a CDATA object
                if isinstance(entry, etree.CDATA):
                    fieldentry.text = entry
                else:
                    fieldentry.text = str(entry)

        assessmentcontrol = etree.SubElement(assessment, 'assessmentcontrol', feedbackswitch='Yes', hintswitch='Yes', solutionswitch='Yes', view='All')

        # Create rubric and its child elements
        rubric = etree.SubElement(assessment, 'rubric', view='All')
        material = etree.SubElement(rubric, 'material')
        mattext = etree.SubElement(material, 'mattext', charset='ascii-us', texttype='text/plain')
        mattext.set('{http://www.w3.org/XML/1998/namespace}space', 'default')

        # Add presentation_material and assessfeedback under assessment
        presentation_material = etree.SubElement(assessment, 'presentation_material')
        flow_mat = etree.SubElement(presentation_material, 'flow_mat', {'class': 'Block'})
        material = etree.SubElement(flow_mat, 'material')
        mattext = etree.SubElement(material, 'mattext', charset='ascii-us', texttype='text/plain')
        mattext.set('{http://www.w3.org/XML/1998/namespace}space', 'default')
        mattext.text = etree.CDATA('')


        # Create the assessfeedback and its children
        assessfeedback = etree.SubElement(assessment, 'assessfeedback', ident='Feedback', title='Feedback', view='All')
        flow_mat = etree.SubElement(assessfeedback, 'flow_mat', {'class': 'Block'})
        material = etree.SubElement(flow_mat, 'material')
        mattext = etree.SubElement(material, 'mattext', charset='ascii-us', texttype='text/plain')
        mattext.set('{http://www.w3.org/XML/1998/namespace}space', 'default')
        mattext.text = ''


        # Add a section under assessment
        section = etree.SubElement(assessment, 'section', ident='11083', title='Default')

        qtimetadata = etree.SubElement(section, 'qtimetadata')

        field_labels = ["SECTION_INFORMATION", "SECTION_OBJECTIVE", "SECTION_KEYWORD", "SECTION_RUBRIC", "ATTACHMENT", "QUESTIONS_ORDERING"]

        for label in field_labels:
            qtimetadatafield = etree.SubElement(qtimetadata, 'qtimetadatafield')
            fieldlabel = etree.SubElement(qtimetadatafield, 'fieldlabel')
            fieldlabel.text = label
            fieldentry = etree.SubElement(qtimetadatafield, 'fieldentry')
            if label == "QUESTIONS_ORDERING":
                fieldentry.text = "1"

        presentation_material = etree.SubElement(section, 'presentation_material')
        flow_mat = etree.SubElement(presentation_material, 'flow_mat', attrib={"class": "Block"})

        material = etree.SubElement(flow_mat, 'material')
        mattext = etree.SubElement(material, 'mattext', attrib={"charset": "ascii-us", "texttype": "text/plain", "{http://www.w3.org/XML/1998/namespace}space": "default"})

        material = etree.SubElement(flow_mat, 'material')
        matimage = etree.SubElement(material, 'matimage', attrib={"embedded": "base64", "imagtype": "text/html", "uri": ""})

        selection_ordering = etree.SubElement(section, 'selection_ordering', attrib={"sequence_type": "Normal"})
        selection = etree.SubElement(selection_ordering, 'selection')
        sourcebank_ref = etree.SubElement(selection, 'sourcebank_ref')
        selection_number = etree.SubElement(selection, 'selection_number')
        order = etree.SubElement(selection_ordering, 'order', attrib={"order_type": "Sequential"})

        id = 10000

        for q in questions: 
            item = etree.SubElement(section, 'item', attrib={"ident": str(id), "title": "Essay Question"})
            id += 1
            qticomment = etree.SubElement(item, 'qticomment')
            duration = etree.SubElement(item, 'duration')

            itemmetadata = etree.SubElement(item, 'itemmetadata')
            qtimetadata = etree.SubElement(itemmetadata, 'qtimetadata')

            field_labels = ["qmd_itemtype", "TEXT_FORMAT", "ITEM_OBJECTIVE", "ITEM_KEYWORD", "ITEM_RUBRIC", "ITEM_TAGS", "ATTACHMENT"]
            field_entries = ["Essay", "HTML", "", "", "", "", ""]

            for label, entry in zip(field_labels, field_entries):
                qtimetadatafield = etree.SubElement(qtimetadata, 'qtimetadatafield')
                fieldlabel = etree.SubElement(qtimetadatafield, 'fieldlabel')
                fieldlabel.text = label
                fieldentry = etree.SubElement(qtimetadatafield, 'fieldentry')
                fieldentry.text = entry

            rubric = etree.SubElement(item, 'rubric', attrib={"view": "All"})
            material = etree.SubElement(rubric, 'material')
            mattext = etree.SubElement(material, 'mattext', attrib={"charset": "ascii-us", "texttype": "text/plain", "{http://www.w3.org/XML/1998/namespace}space": "default"})

            presentation = etree.SubElement(item, 'presentation', attrib={"label": "Model Short Answer"})
            flow = etree.SubElement(presentation, 'flow', attrib={"class": "Block"})
            material = etree.SubElement(flow, 'material')
            mattext = etree.SubElement(material, 'mattext', attrib={"charset": "ascii-us", "texttype": "text/plain", "{http://www.w3.org/XML/1998/namespace}space": "default"})
            mattext.text = q

            resprocessing = etree.SubElement(item, 'resprocessing')
            outcomes = etree.SubElement(resprocessing, 'outcomes')
            decvar = etree.SubElement(outcomes, 'decvar', attrib={"defaultval": "0", "maxvalue": "4.0", "minvalue": "0.0", "varname": "SCORE", "vartype": "Integer"})

            feedback_idents = ["Correct", "InCorrect"]
            for ident in feedback_idents:
                itemfeedback = etree.SubElement(item, 'itemfeedback', attrib={"ident": ident, "view": "All"})
                flow_mat = etree.SubElement(itemfeedback, 'flow_mat', attrib={"class": "Block"})
                material = etree.SubElement(flow_mat, 'material')
                mattext = etree.SubElement(material, 'mattext', attrib={"charset": "ascii-us", "texttype": "text/plain", "{http://www.w3.org/XML/1998/namespace}space": "default"})


        tree = etree.ElementTree(root)

        # EXPORT
        tree.write('output.xml', pretty_print=True, xml_declaration=True, encoding='UTF-8')




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
            results += result.get('generated_questions')[0].get('questions')

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
