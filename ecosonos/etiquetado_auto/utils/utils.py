import os
import json
import numpy as np
from etiquetado_auto.models import GuardadoClusterResult


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


def serialize_and_save_to_db(data):
    data_to_save = []
    for item in data:
        parsed_item = []
        for value in item:
            if isinstance(value, np.ndarray):
                value = value.tolist()

            parsed_item.append(value)

        data_to_save.append(parsed_item)

    serialized_data = json.dumps(data_to_save)
    new_specs_db = GuardadoClusterResult(data=serialized_data)
    return new_specs_db.save()


def deserialize_from_db():
    retrieved_data = GuardadoClusterResult.objects.first()
    retrieved_json_data = json.loads(retrieved_data.data)

    reconstructed_data = []
    for item in retrieved_json_data:
        reconstructed_item = []
        for value in item:
            if isinstance(value, list):
                # Convert Python list to NumPy array
                value = np.array(value)
            reconstructed_item.append(value)
        reconstructed_data.append(reconstructed_item)

    reconstructed_data = np.array(reconstructed_data)
    return reconstructed_data
