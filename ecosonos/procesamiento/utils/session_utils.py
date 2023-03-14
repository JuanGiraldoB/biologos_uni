def inicializar_variables_session(request, ruta, grabaciones, n_grabaciones, PSD_medio):
    print("cargando archivos")
    request.session['ruta'] = ruta
    request.session['grabaciones'] = grabaciones
    request.session['n_grab'] = n_grabaciones
    request.session['index'] = 0

    request.session['PSD_medio'] = PSD_medio
    print('archivos cargados')
