import os


def prepare_csv_table_name(selected_folders_basenames, destination_folder):
    csv_name = 'Tabla_Nuevas_especies'
    for nombre in selected_folders_basenames:
        csv_name += f'_{nombre}'

    csv_name = os.path.join(destination_folder, f'{csv_name}.csv')

    return csv_name
