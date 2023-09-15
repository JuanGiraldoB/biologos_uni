import datetime


def save_indices_session(request, selected_indices):
    request.session['indices_seleccionados'] = selected_indices


def get_indices_session(request):
    return request.session['indices_seleccionados']


def save_to_txt(txt_path, file_name):
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(txt_path, 'a') as file:
            file.write(f"{file_name} ---- {current_time}\n")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
