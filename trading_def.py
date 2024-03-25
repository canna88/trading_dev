# IMPORT LIBRERIE
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# CREAZIONE DELLE CARTELLE DI DESTINAZIONE DEI FILE (nel caso non esistessero):
# -"folder_1" -> primo periodo di comparazione
# -"folder_2" -> secondo periodo di comparazione
# -"folder_result" -> salva i risultati delle segnalazioni
if not os.path.exists('folder_1'):
    os.makedirs('folder_1')
if not os.path.exists('folder_2'):
    os.makedirs('folder_2')
if not os.path.exists('folder_results'):
    os.makedirs('folder_results')

# DEFINIZIONE DELLE FUNZIONI (se vuoi dargli un'occhiata non ci sono problemi,
# sennò puoi saltare fino in fondo dove c'è la parte dei parametri personalizzati)

# FUNZIONE PER IL DOWNLOAD DEI DATI
def download_data(data, start, end, inter):
    data_asset = yf.download(data, start=start, end=end, interval=inter)
    data_asset.drop(['Adj Close'], axis=1, inplace=True)
    return pd.DataFrame(data_asset)

# FUNZIONE PER L'INVIO DELLA MAIL
def send_email_with_attachment(email_from, password, email_to, array):
    if len(array) != 0:
        # Converti la lista in un DataFrame di Pandas e salva il DataFrame come file CSV
        confirmed_signal_df = pd.DataFrame(array, columns=['Confirmed Signal']) 
        confirmed_signal_df.to_csv("signal.csv", index=False)
        # Define the HTML document
        html = '''
            <html>
                <body>
                    <h1>doppio minimo weekly</h1>
                </body>
            </html>
            '''

        # Define a function to attach files as MIMEApplication to the email

        def attach_file_to_email(email_message, filename):
            # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
            with open(filename, "rb") as f:
                file_attachment = MIMEApplication(f.read())
            # Add header/name to the attachments    
            file_attachment.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            # Attach the file to the message
            email_message.attach(file_attachment)


        # Generate today's date to be included in the email Subject
        date_str = pd.Timestamp.today().strftime('%Y-%m-%d')

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = f'doppio minimo weekly - {date_str}'

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Attach more (documents)
        attach_file_to_email(email_message, "signal.csv")
        # Convert it as a string
        email_string = email_message.as_string()

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_string) 
            
        print("File inviato")
    else:
        print("Non ci sono dati")

# FUNZIONE GET STOCK DATA
# Questa è la funzione più importate: prende tutti i parametri personalizzati,
# valuta se vuoi fare un'analisi su "giornaliero", "settimanale" o "mensile"
# a seconda dei parametri scelti, salva i file nelle cartelle e invia la mail solo
# se è presente un segnale

def get_stock_data(data_rif, array, time, difference, folder1, folder2, folder_result):
    data_riferimento = data_rif
    interval = '1d'
    
    if time == 'giornaliero':
        #Inizializzazione dell'array delle segnalazioni sul "giornaliero"
        conferma_segnale_giornaliero = []
        
        # Identifico il periodo di comparazione
        data_5_giorni_fa = data_riferimento - timedelta(days=5)
        start_date= data_5_giorni_fa
        end_date = data_riferimento + timedelta(days=1)

        for name in array: 
            stock_data = download_data(name, start_date, end_date, interval)
            
            # Identificazione del min1 (primo periodo di comparazione)
            last_row = stock_data.iloc[-1] # Ottieni l'ultima riga di stock_data
            stock_data1 = pd.DataFrame([last_row], columns=stock_data.columns)
            stock_data1.to_csv(f'{folder1}/{name}_giornaliero.csv')
            min1=stock_data1['Low'].min()

            # Identificazione del min2 (secondo periodo di comparazione)
            penultimate_row = stock_data.iloc[-2] # Ottieni la penultima riga di stock_data
            stock_data2 = pd.DataFrame([penultimate_row], columns=stock_data.columns)           
            stock_data2.to_csv(f'{folder2}/{name}_giornaliero_2.csv')
            min2=stock_data2['Low'].min()
            
            # Calcolo la differenza tra il min1 e il min2
            diff = (abs(min1 - min2) / min1) * 100
            
            # Se il segnale è valido, aggiungo all'array
            if min1 == min2 or (min2 > min1 and diff <= difference):
                conferma_segnale_giornaliero.append(name)
                  
        if len(conferma_segnale_giornaliero) != 0:
            conferma_segnale_giornaliero_df = pd.DataFrame(conferma_segnale_giornaliero, columns=["conferma_segnale_giornaliero"])
            conferma_segnale_giornaliero_df.to_csv(f'{folder_result}/{name}_giornaliero.csv')
            # INVIO LA MAIL
            send_email_with_attachment(email_from, password, email_to,conferma_segnale_giornaliero)
        print("array definitivo_giornaliero: ",conferma_segnale_giornaliero)
        
        
            
    elif time == 'settimanale':
        #Inizializzazione dell'array delle segnalazioni sul "settimanale"
        conferma_segnale_settimanale = []
        
        # Identifico il periodo di comparazione
        primo_lunedi = data_riferimento
        while primo_lunedi.weekday() != 0:  # 0 rappresenta il venerdì
            primo_lunedi -= timedelta(days=1)
        start_date1= primo_lunedi
        end_date1 = data_riferimento + timedelta(days=1)
        start_date2 = primo_lunedi - timedelta(days=7)
        end_date2 = start_date2 + timedelta(days=6)
        

        for name in array: 
            # Identificazione del min1 (primo periodo di comparazione)
            stock_data1 = download_data(name, start_date1, end_date1, interval)            
            stock_data1.to_csv(f'{folder1}/{name}_settimanale.csv')
            min1=stock_data1['Low'].min()
            
            # Identificazione del min2 (secondo periodo di comparazione)
            stock_data2 = download_data(name, start_date2, end_date2, interval)            
            stock_data2.to_csv(f'{folder2}/{name}_settimanale_2.csv')
            min2=stock_data2['Low'].min()
            
            # Calcolo la differenza tra il min1 e il min2
            diff = (abs(min1 - min2) / min1) * 100
            
            # Se il segnale è valido, aggiungo all'array
            if min1 == min2 or (min2 > min1 and diff <= difference):
                conferma_segnale_settimanale.append(name)
        
        if len(conferma_segnale_settimanale) != 0:
            conferma_segnale_settimanale = pd.DataFrame(conferma_segnale_settimanale, columns=["conferma_segnale_settimanale"])
            conferma_segnale_settimanale.to_csv(f'{folder_result}/{name}_settimanle.csv')    
            # INVIO LA MAIL
            send_email_with_attachment(email_from, password, email_to,conferma_segnale_settimanale)
        
        print("array definitivo_settimanale: ",conferma_segnale_settimanale)
        

    elif time =='mensile':
        #Inizializzazione dell'array delle segnalazioni sul "mensile"
        conferma_segnale_mensile = []
        
        # Identifico il periodo di comparazione
        start_date1 = data_riferimento.replace(day=1)
        end_date1 = data_riferimento + timedelta(days=1)
        data_mese_precedente = data_riferimento.replace(day=1) - timedelta(days=1)
        start_date2 = data_mese_precedente.replace(day=1)
        end_date2 = start_date1
        
        for name in array: 
            # Identificazione del min1 (primo periodo di comparazione)
            stock_data1 = download_data(name, start_date1, end_date1, interval)            
            stock_data1.to_csv(f'{folder1}/{name}_mensile.csv')
            min1=stock_data1['Low'].min()

            # Identificazione del min2 (secondo periodo di comparazione)
            stock_data2 = download_data(name, start_date2, end_date2, interval)            
            stock_data2.to_csv(f'{folder2}/{name}_mensile_2.csv')
            min2=stock_data2['Low'].min()
            
            # Calcolo la differenza tra il min1 e il min2
            diff = (abs(min1 - min2) / min1) * 100
            
            # Se il segnale è valido, aggiungo all'array
            if min1 == min2 or (min2 > min1 and diff <= difference):
                conferma_segnale_mensile.append(name)
        
        if len(conferma_segnale_mensile) != 0:
            conferma_segnale_mensile = pd.DataFrame(conferma_segnale_mensile, columns=["conferma_segnale_mensile"])
            conferma_segnale_mensile.to_csv(f'{folder_result}/{name}_mensile.csv') 
            # INVIO LA MAIL
            send_email_with_attachment(email_from, password, email_to,conferma_segnale_mensile)
        print("array definitivo_mensile: ",conferma_segnale_mensile)
        

# PARAMETRI: DA MODIFICARE SECONDO LE ESIGENZE
email_from = 'fabrytrader71@gmail.com'
password = 'rtggxvrgitgriqaj'
email_to = 'fa.pallotta@gmail.com'
lista_stocks = ['A2A.MI','FM.MI','AMP.MI'] # Lista delle stocks da analizzare
url_folder1 = "folder_1" # Inserire il percorso della folder_1
url_folder2 = "folder_2" # Inserire il percorso della folder_2
url_folder_result= "folder_results" # Inserire il percorso della folder_result

max_diff= 0.5 # Inserire la differenza percentuale del segnale
time_options = ['giornaliero', 'settimanale', 'mensile']

data_odierna = datetime.now().date()
data_personalizzata = '2024-01-01' 

# LANCIO DELLE FUNZIONI:
# - puoi lanciarne quante ne vuoi, basta copiare una delle righe e impostare il tipo di analisi da effettuare:
    # - "giornaliero"
    # - "settimanale"
    # - "mensile"
# - nel caso in cui volessi far partire le funzioni da una data diversa da quella odierna:
# cambia il primo parametro della funzione con "data_personalizzata",
# naturalmente puoi cambiare la "data_personalizzata" pochi righe sopra

get_stock_data(data_odierna, lista_stocks, "giornaliero", max_diff, url_folder1,url_folder2, url_folder_result)
get_stock_data(data_odierna, lista_stocks, "settimanale", max_diff, url_folder1,url_folder2, url_folder_result)
get_stock_data(data_odierna, lista_stocks, "mensile", max_diff, url_folder1, url_folder2, url_folder_result)
