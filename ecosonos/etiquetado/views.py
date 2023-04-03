from django.shortcuts import render

# Create your views here.


def etiquetado(request):
    return render(request, 'etiquetado/etiquetado.html')
