import os


def prepare_csv_path(selected_folders_basenames, destination_folder, table_type):
    if table_type == 'sonotipo':
        csv_name = 'Tabla_Nuevas_especies'
    else:
        csv_name = 'Tabla_reconocimiento'

    for nombre in selected_folders_basenames:
        csv_name += f'_{nombre}'

    csv_name = os.path.join(destination_folder, f'{csv_name}.csv')

    return csv_name


def save_cluster_names_session(request, cluster_names):
    request.session['cluster_names'] = cluster_names


def get_cluster_names_session(request):
    return request.session['cluster_names']
