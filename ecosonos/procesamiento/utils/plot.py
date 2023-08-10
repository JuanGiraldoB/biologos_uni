import pandas as pd
import plotly.express as px
from ecosonos.utils.archivos_utils import get_date_from_filename
import os


def get_plot(csv_folder):
    # Step 1: Read the xlsx file and extract the necessary information
    csv_path = os.path.join(csv_folder, 'resultado_preproceso.csv')
    df = pd.read_csv(csv_path)

    # Step 2: Extract the date from the filename using the function `get_date_from_filename`
    df['Date'] = df['name_FI'].apply(get_date_from_filename)

    # Step 3: Sort the DataFrame by the 'Date' column
    df = df.sort_values(by='Date')

    fig = px.scatter(df, x='Date', y='field_number_PR',
                     color='rain_FI', height=300)

    fig = fig.to_html()

    return fig
