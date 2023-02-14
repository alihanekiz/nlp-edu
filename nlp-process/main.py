import spacy

f = open('../clean-data/lecture-data/content_w01.txt', 'r')
nlp = spacy.load("en_core_web_sm")
s = list()


while True: 
    l = f.readline()
    
    if not l:
        break

    l = l.replace(u'\xa0', u' ')
    l = l.strip()

    if l != '':
        s.append(l)


for line in s: 
    doc = nlp(line)
    for np in doc.noun_chunks:
        print(np.text)