# LIBRARY IMPORTS
import os
import sys
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


# Add paths to custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'functions')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'list_of_stocks')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'parameters')))

# Import functions from custom modules
from functions import download_data, send_email_with_attachment, get_stock_data, get_stock_data
from list_of_stocks import lista_stocks_ita, lista_stocks_sp_500, lista_stocks_russell_2000, lista_test
from parameters import is_save, email_from, password, email_to, max_diff, url_folder_1st_period, url_folder_2nd_period, url_folder_result, data_odierna,data_personalizzata_giornaliera, data_personalizzata_settimana, data_personalizzata_mensile, indicators_params

# CREATE DESTINATION FOLDERS FOR FILES (if they do not exist):
# - "folder_1" -> first comparison period
# - "folder_2" -> second comparison period
# - "folder_result" -> save signal results
if not os.path.exists(url_folder_1st_period):
    os.makedirs(url_folder_1st_period)
if not os.path.exists(url_folder_2nd_period):
    os.makedirs(url_folder_2nd_period)
if not os.path.exists(url_folder_result):
    os.makedirs(url_folder_result)

# FUNCTION EXECUTION:

get_stock_data(data_personalizzata_giornaliera, lista_test, "giornaliero", max_diff, is_save, url_folder_1st_period, url_folder_2nd_period, url_folder_result,indicators_params)
get_stock_data(data_personalizzata_settimana, lista_test, "settimanale", max_diff, is_save, url_folder_1st_period, url_folder_2nd_period, url_folder_result,indicators_params)
get_stock_data(data_personalizzata_mensile, lista_test, "mensile", max_diff, is_save, url_folder_1st_period, url_folder_2nd_period, url_folder_result,indicators_params)