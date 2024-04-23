# IMPORT LIBRERIE
import pandas as pd
import yfinance as yf
from datetime import timedelta
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import math
import talib


# DEFINIZIONE DELLE FUNZIONI (se vuoi dargli un'occhiata non ci sono problemi,
# sennò puoi saltare fino in fondo dove c'è la parte dei parametri personalizzati)

# FUNZIONE PER IL DOWNLOAD DEI DATI
def download_data(data, start, end, inter):
    data_asset = yf.download(data, start=start, end=end, interval=inter)
    data_asset.drop(['Adj Close'], axis=1, inplace=True)
    return pd.DataFrame(data_asset)

# FUNZIONE PER L'INVIO DELLA MAIL
def send_email_with_attachment(nome_segnale,data_analisi,email_from, password, email_to, array):

    if len(array) != 0:
        # Generate today's date to be included in the email Subject
        date_str = data_analisi
        confirmed_signal_df = array

        confirmed_signal_df.to_csv(f'DOPPIO MINIMO - {nome_segnale} - Data analisi: {date_str.strftime("%Y-%m-%d")}.csv', index=False)
        # Define the HTML document
        html = f'''
            <html>
                <body>
                    <h1>DOPPIO MINIMO - {nome_segnale} - Data analisi: {date_str.strftime('%Y-%m-%d')} </h1>
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




        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart()
        email_message['From'] = email_from
        email_message['To'] = email_to
        email_message['Subject'] = f'Doppio minimo {nome_segnale} - Data analisi: {date_str.strftime("%Y-%m-%d")}'

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        # Attach more (documents)
        attach_file_to_email(email_message, f'DOPPIO MINIMO - {nome_segnale} - Data analisi: {date_str.strftime("%Y-%m-%d")}.csv')
        # Convert it as a string
        email_string = email_message.as_string()

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_string)

        print(f"File inviato - {nome_segnale} - Data analisi: {date_str.strftime('%Y-%m-%d')}")
    else:
        print(f"Non ci sono dati - {nome_segnale} - Data analisi: {date_str.strftime('%Y-%m-%d')}")

# FUNZIONE GET STOCK DATA
# Questa è la funzione più importate: prende tutti i parametri personalizzati,
# valuta se vuoi fare un'analisi su "giornaliero", "settimanale" o "mensile"
# a seconda dei parametri scelti, salva i file nelle cartelle e invia la mail solo
# se è presente un segnale

def get_stock_data(data_rif, array, time, difference, is_save,folder1, folder2, folder_result, indicators_params):
    data_riferimento = data_rif

    interval_day = '1d'
    interval_weekly = '1wk'
    interval_monthly = '1mo'
    
    # Accedi ai parametri dell'indicatore dal dizionario
    RSI_period = indicators_params["RSI_period"]
    MACD_period_fast = indicators_params["MACD_period_fast"]
    MACD_period_slow = indicators_params["MACD_period_slow"]
    MACD_period_signal = indicators_params["MACD_period_signal"]
    MOM_period = indicators_params["MOM_period"]
    SMA14_period = indicators_params["SMA14_period"]
    SMA50_period = indicators_params["SMA50_period"]
    SMA200_period = indicators_params["SMA200_period"]
    SAR_acceleration = indicators_params["SAR_acceleration"]
    SAR_maximum_acceleration = indicators_params["SAR_maximum_acceleration"]
    ADX_period = indicators_params["ADX_period"]
    BBANDS_period = indicators_params["BBANDS_period"]
    BBANDS_nbdevup = indicators_params["BBANDS_nbdevup"]
    BBANDS_nbdevdn = indicators_params["BBANDS_nbdevdn"]
    BBANDS_matype = indicators_params["BBANDS_matype"]
        
    # Calcolo il periodo massimo tra tutti gli indicatori per identificare il periodo massimo di download da utilizzare
    max_period = max(RSI_period, MACD_period_fast, MACD_period_slow,MACD_period_signal,MOM_period,SMA14_period,SMA50_period,
                     SMA200_period,ADX_period,BBANDS_period,BBANDS_nbdevup,BBANDS_nbdevdn,BBANDS_matype)
    
    def calculate_indicators(dataframe):
        dataframe["RSI"] = talib.RSI(dataframe["Close"], timeperiod=RSI_period)
        dataframe["MACD"],dataframe["MACD_signal"],dataframe["MACD_hist"]= talib.MACD(dataframe["Close"],fastperiod=MACD_period_fast, slowperiod=MACD_period_slow, signalperiod=MACD_period_signal)
        dataframe["MOM"] = talib.MOM(dataframe["Close"], timeperiod=MOM_period)
        dataframe["MM14"] = talib.SMA(dataframe["Close"], timeperiod=SMA14_period)
        dataframe["MM50"] = talib.SMA(dataframe["Close"], timeperiod=SMA50_period)
        dataframe["MM200"] = talib.SMA(dataframe["Close"], timeperiod=SMA200_period)
        dataframe["SAR"] = talib.SAR(dataframe["High"], dataframe["Low"], acceleration=SAR_acceleration, maximum=SAR_maximum_acceleration)
        dataframe["ADX"] = talib.ADX(dataframe["High"], dataframe["Low"], dataframe["Close"], timeperiod = ADX_period)
        dataframe["BB_upper"],dataframe["BB_middle"],dataframe["BB_lower"] = talib.BBANDS(dataframe["Close"], timeperiod=BBANDS_period, nbdevup=BBANDS_nbdevup, nbdevdn=BBANDS_nbdevdn,matype=BBANDS_matype)
        
        return dataframe
    
    def calculate_last_three_rows(dataframe):
        last_row = dataframe.iloc[-1] # Ottieni l'ultima riga di stock_data
        penultimate_row = dataframe.iloc[-2] # Ottieni la penultima riga di stock_data
        third_last_row = dataframe.iloc[-3] # Ottieni la terza penultima
        return last_row, penultimate_row, third_last_row
    
    def calculate_conditions(dataframe,timeframe):
        if not dataframe.empty:
            # Ottengo le ultime 3 righe del dataframe
            last_row,penultimate_row,third_last_row = calculate_last_three_rows(dataframe)
            
            # Ottengo i dataframe delle ultime 3 righe del dataframe
            stock_data1 = pd.DataFrame([last_row], columns=dataframe.columns)
            stock_data2 = pd.DataFrame([penultimate_row], columns=dataframe.columns)
            stock_data3 = pd.DataFrame([third_last_row], columns=dataframe.columns)
            
            close1 = stock_data1["Close"].iloc[0]
            close2 = stock_data2["Close"].iloc[0]
            close3 = stock_data3["Close"].iloc[0]
            open1 = stock_data1["Open"].iloc[0]
            open2 = stock_data2["Open"].iloc[0]
            
            min1=stock_data1['Low'].min()
            min2=stock_data2['Low'].min()

            
            # Identificazione del min1 (primo periodo di comparazione)
            stock_data1["BORSA"] = ((close1 - close2)/close2) * 100
            print(stock_data1)
            print(f'{folder1}/{name}_{timeframe}.csv')
            stock_data1.to_csv(f'{folder1}/{name}_{timeframe}.csv') if is_save == True else None
            
            
            # Identificazione del min2 (secondo periodo di comparazione)
            stock_data2["BORSA"] = ((close2 - close3)/close3) * 100
           
            stock_data2.to_csv(f'{folder2}/{name}_{timeframe}_2.csv') if is_save == True else None
                       
            
            # Calcolo la differenza tra il min1 e il min2
            diff = (abs(min1 - min2) / min1) * 100
            cond_1 = min1 == min2
            cond_2 = diff <= difference #min2 > min1 and diff <= difference
            cond_3 = (open1 < close1)
            cond_4 = (open2 > close2)
            cond_5 = (close1 > close2)
            cond_total = cond_5 and cond_3 and cond_4 and (cond_1 or cond_2)
                       
            print(cond_total)
            return cond_total
        
            
    if time == 'giornaliero':
        #Inizializzazione dell'array delle segnalazioni sul "giornaliero"
        conferma_segnale_giornaliero = []

        # Identifico il periodo di comparazione
        periodo_daily = (math.ceil(max_period / 5)) * 7
        print("Data riferimento:",data_riferimento)
        start_date= data_riferimento - timedelta(days=max(periodo_daily *1.2,60))
        end_date = data_riferimento + timedelta(days=1)
       
        for name in array:
            stock_data = download_data(name, start_date, end_date, interval_day)
            stock_data = calculate_indicators(stock_data)
            condizione_verificata = calculate_conditions(stock_data,"giornaliero")

            # Se il segnale è valido, aggiungo all'array
            if condizione_verificata:
                conferma_segnale_giornaliero.append(name)
            else:
                print(f"Segnale non valido: {name}")
                print("Conferma segnale giornaliero",conferma_segnale_giornaliero)

        if len(conferma_segnale_giornaliero) != 0:
            print(conferma_segnale_giornaliero)
            print("array definitivo_giornaliero ok")
            conferma_segnale_giornaliero_df = pd.DataFrame(conferma_segnale_giornaliero, columns=["conferma_segnale_giornaliero"])
            conferma_segnale_giornaliero_df.to_csv(f'{folder_result}/DOPPIO MINIMO - giornaliero {data_riferimento.strftime("%Y-%m-%d")}.csv') if is_save == True else None
            print(conferma_segnale_giornaliero_df)
        
            # INVIO LA MAIL
            send_email_with_attachment("Giornaliero", data_riferimento,email_from, password, email_to,conferma_segnale_giornaliero_df)
            print("array definitivo_giornaliero: ",conferma_segnale_giornaliero_df)



    elif time == 'settimanale':
        #Inizializzazione dell'array delle segnalazioni sul "settimanale"
        conferma_segnale_settimanale = []      

        periodo_weekly = (math.ceil(max_period / 5)) * 7
        
        # Identifico il periodo di comparazione
        primo_lunedi = data_riferimento
        while primo_lunedi.weekday() != 0:  # 0 rappresenta il lunedi
            primo_lunedi -= timedelta(days=1)
        start_date1= primo_lunedi
        end_date1 = start_date1 + timedelta(days=6)
        start_date2 = primo_lunedi - timedelta(days=7)
        end_date2 = start_date2 + timedelta(days=6)
        
        start_date_test = start_date2 - timedelta(days= (periodo_weekly * 7 + 15))


        for name in array:
            # Identificazione del min1 (primo periodo di comparazione)
            stock_data = download_data(name, start_date_test, end_date1, interval_weekly)
            stock_data = calculate_indicators(stock_data)
            condizione_verificata = calculate_conditions(stock_data,"settimanale")
            
            # Se il segnale è valido, aggiungo all'array
            if condizione_verificata:
                conferma_segnale_settimanale.append(name)
            else:
                print(f"Segnale non valido: {name}")
                print("Conferma segnale settimanale",conferma_segnale_settimanale)

        if len(conferma_segnale_settimanale) != 0:
            conferma_segnale_settimanale_df = pd.DataFrame(conferma_segnale_settimanale, columns=["conferma_segnale_settimanale"])
            conferma_segnale_settimanale_df.to_csv(f'{folder_result}/DOPPIO MINIMO - settimanale - {data_riferimento.strftime("%Y-%m-%d")}.csv') if is_save == True else None
            # INVIO LA MAIL
            send_email_with_attachment("Settimanale",data_riferimento,email_from, password, email_to,conferma_segnale_settimanale_df)

            print("array definitivo_settimanale: ",conferma_segnale_settimanale_df)


    elif time =='mensile':
        #Inizializzazione dell'array delle segnalazioni sul "mensile"
        conferma_segnale_mensile = []
        periodo_monthly = (math.ceil(max_period / 5)) * 7
        
        

        # Identifico il periodo di comparazione
        start_date1 = data_riferimento.replace(day=1)
        end_date1 = data_riferimento + timedelta(days=1)
        data_mese_precedente = data_riferimento.replace(day=1) - timedelta(days=1)
        start_date2 = data_mese_precedente.replace(day=1)
        end_date2 = start_date1

        start_date_test = (start_date2 - timedelta(days= periodo_monthly*31)).replace(day=1)

        for name in array:
            stock_data = download_data(name, start_date_test, end_date1, interval_monthly)
            stock_data = calculate_indicators(stock_data)
            condizione_verificata = calculate_conditions(stock_data,"mensile")
                

            # Se il segnale è valido, aggiungo all'array
            if condizione_verificata:
                conferma_segnale_mensile.append(name)
            else:
                print(f"Segnale non valido: {name}")
                print("Conferma segnale mensile",conferma_segnale_mensile)
                
        if len(conferma_segnale_mensile) != 0:
            conferma_segnale_mensile_df = pd.DataFrame(conferma_segnale_mensile, columns=["conferma_segnale_mensile"])
            conferma_segnale_mensile_df.to_csv(f'{folder_result}/DOPPIO MINIMO - mensile - {data_riferimento.strftime("%Y-%m-%d")}.csv') if is_save == True else None
            # INVIO LA MAIL
            send_email_with_attachment("Mensile",data_riferimento,email_from, password, email_to,conferma_segnale_mensile_df)
            print("array definitivo_mensile: ",conferma_segnale_mensile_df) 