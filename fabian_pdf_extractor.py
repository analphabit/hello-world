import pdfplumber
import pandas as pd

# Define empty list for all highlights
highlights = []

# drei neue Listen
highlights_text = []
highlights_rect_top = []
highlights_rect_bottom = []

# Define page number, starting 0
pagenumber = 0


# Open the PDF file
with pdfplumber.open("konfitag2.pdf") as pdf:
    # Iterate over the pages in the PDF
    for page in pdf.pages:
        pagenumber += 1 # increase page number

        # Extract the annotations from the page
        rectangles = page.rects
        # Iterate over the annotations
        #print(len(annotations))

        text = ''
        for id, rec in enumerate(rectangles):
        #for rec in rectangles:
            #print(rec['x0'], rec['top'], rec['x1'], rec['bottom'])

            #if rec['bottom']-rec['top'] > -3 #Wenn abstand der letzen beiden rectangles kleiner als 3 Pixel, wird es als eines gerechnet - MUSS MIT INDEX DES VORHERIGEN EINTRAGS VERSEHEN WERDEN!

            this_rect = page.crop((rec['x0'], rec['top'], rec['x1'], rec['bottom']))

            if this_rect.extract_text(): # if string not empty
                text += ' '+this_rect.extract_text()
                highlights.append([pagenumber, id,  this_rect.extract_text()])
                
                # füge den drei vorher definierten Listen den Text sowie die Top- und Bottom-Koordinaten hinzu
                highlights_text.append(this_rect.extract_text().strip())
                highlights_rect_top.append(rec['top'])
                highlights_rect_bottom.append(rec['bottom'])

        text = " ".join(text.split()) # Remove Double Spaces

# Erstellen eines Dataframes data_df aus den drei neuen Listen
# 1. Schritt: Zippen der drei Listen
zipped_lists = list(zip(highlights_text, highlights_rect_top, highlights_rect_bottom))

# 2. Schritt: Zusammenbau des Dataframes
data_df = pd.DataFrame(zipped_lists, columns = ['Text', 'Top-Koord', 'Bottom-Koord'])


# füge eine neue Spalte "Gruppen-Marker" hinzu, die erstmal mit None-Values gefüllt ist
data_df['Gruppen-Marker'] = None

# setze den "Gruppen-Marker" in der ersten Zeile auf 1
data_df.at[0, 'Gruppen-Marker'] = 1

# Iterieren Sie über den Dataframe
for i in range(1, len(data_df)):
    # Prüfe, ob die Top-Koordinate in der aktuellen Zeile um maximal 16 größer ist als in der vorherigen Zeile
    if data_df.at[i, 'Top-Koord'] - data_df.at[i-1, 'Top-Koord'] <= 16:
        # Setze den Gruppen-Marker auf den Wert der vorherigen Zeile
        data_df.at[i, 'Gruppen-Marker'] = data_df.at[i-1, 'Gruppen-Marker']
    else:
        # Setze den Gruppen-Marker auf einen neuen Wert, der um +1 höher liegt
        data_df.at[i, 'Gruppen-Marker'] = data_df.at[i-1, 'Gruppen-Marker'] + 1
        

# Bevor die Daten weiterverarbeitet werden, wird vor jeder Textzeile noch ein Leerzeichen eingefügt
data_df['Text'] = ' ' + data_df['Text']

# Gruppiere die Daten je "Gruppen-Marker" - dabei wird der Text aus allen Zeilen mit selbem Gruppen-Marker addiert  
# da die Summe der Koords unerheblich ist, wird der Dataframe vor dem Gruppieren via [[Spalte1, Spalte2]] auf die Spalten "Text" und "Gruppenmarker" reduziert
data_grouped_df = data_df[['Text', 'Gruppen-Marker']].groupby('Gruppen-Marker').sum().reset_index()

# Leerzeichen an Beginn oder Ende jedes zusammengefügten Textes können via .strip() entfernt werden
data_grouped_df['Text'] = data_grouped_df['Text'].str.strip()

# der folgende Loop gibt den kompletten Text jeder Highlight-Gruppe aus, wobei len(data_grouped_df) die Zeilen des Dataframes ausgibt

for i in range(len(data_grouped_df)):
    
    print('Text der Highlight-Gruppe ' + str(i + 1) + ':\n\n' + data_grouped_df.iloc[i]['Text'] + '\n\n#################\n')
