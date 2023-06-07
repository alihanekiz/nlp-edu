from pdfminer.high_level import extract_text
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dateutil.parser import parse


def is_date(string, fuzzy=False):
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


nlp = spacy.load('en_core_web_sm')

text  = extract_text('../dirty-data/sp_w01.pdf', 'rb')
# Remove blank lines
text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])

filter_words = ['INNSBRUCK', 'Innsbruck', 'UNTERNEHMERISCHE', 'DIE', 'HOCHSCHULE', 'Austria', 'Universitätsstraße','®','M','CI', 'ANAGEM','ENT', 'CENTER','6020','/', 'www.mci.edu', 'office@mci.edu', 'office', '@', 'mci.edu', 'https', ':', '|CC0', 'Creative', 'Commons', 'ZeroTolerance', 'Source', '15']


clean = ""

for line in text.splitlines():
    if is_date(line):
        continue
    
    
    doc = nlp(line)
    for token in doc:
        if token.text not in filter_words and not token.like_url and not token.like_email:
            clean = clean + token.text
    clean = clean + " "

with open('../clean-data/processed/w01-simple.txt', 'w') as f:
    f.write(clean)