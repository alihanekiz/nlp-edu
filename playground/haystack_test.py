import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
from haystack.utils import launch_es, print_questions
from haystack.nodes import QuestionGenerator, BM25Retriever, FARMReader
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.pipelines import (
    QuestionGenerationPipeline,
    RetrieverQuestionGenerationPipeline,
    QuestionAnswerGenerationPipeline,
)

f = open('../clean-data/lecture-data/content_w01.txt','r')

text1 = f.read()
f.close()

docs = [{"content": text1}]

# Initialize document store and write in the documents
document_store = ElasticsearchDocumentStore()
document_store.write_documents(docs)

# # Initialize Question Generator
question_generator = QuestionGenerator()
question_generation_pipeline = QuestionGenerationPipeline(question_generator)

for idx, document in enumerate(document_store):

    print(f"\n * Generating questions for document {idx}: {document.content[:100]}...\n")
    result = question_generation_pipeline.run(documents=[document])
    print_questions(result)


# retriever = BM25Retriever(document_store=document_store)
# rqg_pipeline = RetrieverQuestionGenerationPipeline(retriever, question_generator)

# print(f"\n * Generating questions for documents matching the query 'Arya Stark'\n")
# result = rqg_pipeline.run(query="Arya Stark")
# print_questions(result)