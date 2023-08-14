import os


def prepare_xlsx_table_name(selected_folders_basenames, destination_folder):
    xlsx_name = 'Tabla_Nuevas_especies'
    for nombre in selected_folders_basenames:
        xlsx_name += f'_{nombre}'

    xlsx_name = os.path.join(destination_folder, f'{xlsx_name}.xlsx')

    return xlsx_name
