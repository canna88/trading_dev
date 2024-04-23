# LIBRARY IMPORTS
from datetime import datetime

# PARAMETERS: INDICATORS
indicators_params = {
    "RSI_period": 13,
    "MACD_period_fast": 12,
    "MACD_period_slow": 26,
    "MACD_period_signal": 9,
    "MOM_period": 10,
    "SMA14_period": 14,
    "SMA50_period": 50,
    "SMA200_period": 200,
    "SAR_acceleration": 0,
    "SAR_maximum_acceleration": 0.00,
    "ADX_period": 14,
    "BBANDS_period": 5,
    "BBANDS_nbdevup": 2,
    "BBANDS_nbdevdn": 2,
    "BBANDS_matype": 0
}

# PARAMETERS: MODIFY AS NEEDED
email_from = ""
password = ""
email_to = ""

url_folder1 = "" # Inserire il percorso della folder_1 #valori di oggi
url_folder2 = "" # Inserire il percorso della folder_2 #valori di ieri
url_folder_result= "" # Inserire il percorso della folder_result

# Whether to save the signal results or not
is_save = True

max_diff = 0.5  # Insert the percentage difference of the signal
time_options = ['daily', 'weekly', 'monthly']

data_odierna = datetime.now().date()

data_personalizzata_giornaliera = '2024-04-15'
data_personalizzata_giornaliera = datetime.strptime(data_personalizzata_giornaliera, '%Y-%m-%d')

data_personalizzata_settimana = '2024-04-20'
data_personalizzata_settimana = datetime.strptime(data_personalizzata_settimana, '%Y-%m-%d')

data_personalizzata_mensile = '2024-04-20'
data_personalizzata_mensile = datetime.strptime(data_personalizzata_mensile, '%Y-%m-%d')