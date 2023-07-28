import pandas as pd
import plotly.express as px
from ecosonos.utils.archivos_utils import obtener_fecha


def obtener_plot(carpeta_raiz):
    # Step 1: Read the xlsx file and extract the necessary information
    df = pd.read_excel(carpeta_raiz + "/resultado.xlsx")

    # Step 2: Extract the date from the filename using the function `get_date_from_filename`
    df['Date'] = df['name_FI'].apply(obtener_fecha)

    # Step 3: Sort the DataFrame by the 'Date' column
    df = df.sort_values(by='Date')

    fig = px.scatter(df, x='Date', y='field_number_PR',
                     color='rain_FI', height=300)

    fig = fig.to_html()

    return fig
