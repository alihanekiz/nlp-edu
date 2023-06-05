from pdfminer.high_level import extract_text
import nltk
import spacy

text  = extract_text('../dirty-data/sp_w01.pdf', 'rb')
filter_words = ['INNSBRUCK', 'Innsbruck', 'UNTERNEHMERISCHE', 'DIE', 'HOCHSCHULE', 'Austria', 'Universitätsstraße','®','M','CI', 'ANAGEM','ENT', 'CENTER','6020','/', 'www.mci.edu', 'office@mci.edu']

nltk.download('punkt')

# def wortliste_zu_saetzen(wortliste):
#     text = ' '.join(wortliste)  # Liste von Wörtern in einen Text umwandeln
#     saetze = nltk.sent_tokenize(text)  # Text in Sätze aufteilen
#     saetze_mit_zeichen = [s + '.' for s in saetze]  # Satzzeichen hinzufügen

#     return saetze_mit_zeichen

def removeUnusedText(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    bereinigte_worte = []
    for token in doc:
        # Filtere Satzzeichen, Zahlen, Stoppwörter und Links
        if not token.is_punct and not token.like_num and not token.is_stop and not token.like_url:
            bereinigte_worte.append(token.text)

    bereinigter_text = ' '.join(bereinigte_worte)
    return bereinigter_text

blocks = text.split()

for w in filter_words:
    blocks = [i for i in blocks if i != w]

text = ''
for b in blocks:
    text += '. ' + removeUnusedText(b)

print(text)

#text = removeUnusedText(text)
