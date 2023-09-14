from PyInstaller.utils.hooks import collect_submodules, collect_data_files
# hiddenimports = [collect_submodules('conectividad'), collect_submodules('etiquetado'), collect_submodules(
#     'etiquetado_auto'), collect_submodules('indices'), collect_submodules('procesamiento')]
# datas = [collect_data_files('conectividad'), collect_data_files('etiquetado'), collect_data_files(
#     'etiquetado_auto'), collect_data_files('indices'), collect_data_files('procesamiento')]

hiddenimports = collect_submodules('procesamiento')
datas = collect_data_files('procesamiento')
