# LIBRARY IMPORTS
from datetime import datetime, timedelta

# PARAMETERS: MODIFY AS NEEDED
email_from = 'alessio.canna88@gmail.com'
password = 'qlzm umce hxfh qrgx'
email_to = 'alessio.canna.job@gmail.com'

url_folder_1st_period = "data_results/folder_1st_period"  # Insert the path of folder_1
url_folder_2nd_period = "data_results/folder_2nd_period"  # Insert the path of folder_2
url_folder_result = "data_results/folder_results"  # Insert the path of folder_result

# Whether to save the signal results or not
is_save = False

max_diff = 0.5  # Insert the percentage difference of the signal
time_options = ['daily', 'weekly', 'monthly']

data_odierna = datetime.now().date()
data_personalizzata_settimana = '2024-03-23'
data_personalizzata_settimana = datetime.strptime(data_personalizzata_settimana, '%Y-%m-%d')

data_personalizzata_mensile = '2024-02-29'
data_personalizzata_mensile = datetime.strptime(data_personalizzata_mensile, '%Y-%m-%d')