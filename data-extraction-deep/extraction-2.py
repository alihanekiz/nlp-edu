import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from pdfminer.high_level import extract_text

# Load NLTK stop words
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Add your custom words to stop words list
custom_stopwords = ['INNSBRUCK', 'Innsbruck', 'UNTERNEHMERISCHE', 'DIE', 'HOCHSCHULE', 'Austria', 'Universitätsstraße','®','M','CI', 'ANAGEM','ENT', 'CENTER','6020','/', 'www.mci.edu', 'office@mci.edu']
stop_words.update(custom_stopwords)

# Load Spacy model
nlp = spacy.load('en_core_web_sm')

def clean_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Remove stopwords
    tokens = [word for word in tokens if not word in stop_words]

    # Lowercase and remove non-alphabetical characters
    tokens = [word.lower() for word in tokens if word.isalpha()]
    
    
    # Lemmatization
    doc = nlp(' '.join(tokens))
    tokens = [token.lemma_ for token in doc]
    
    # Join words back into text
    cleaned_text = ' '.join(tokens)
    
    return cleaned_text

# Read the file
text = extract_text('../dirty-data/sp_w01.pdf', 'rb')


# Clean the text
cleaned_text = clean_text(text)

# Write cleaned text back into the file
with open('../clean-data/processed/w01.txt', 'w') as f:
    f.write(cleaned_text)