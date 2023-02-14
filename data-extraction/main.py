# importing required modules
from PyPDF2 import PdfReader
text = ""

reader = PdfReader('../dirty-data/sp_w01.pdf')
 
# getting a specific page from the pdf file
for page in reader.pages:
    newText = page.extract_text()
    newText = newText.replace('MCI MANAGEMENT CENTER INNSBRUCK Universitätsstraße 15 office@mci.edu', '')
    newText = newText.replace('DIE UNTERNEHMERISCHE HOCHSCHULE® 6020 Innsbruck  / Austria www.mci. edu', '')
    print(newText)
    text = text + newText

