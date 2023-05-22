from django.shortcuts import render

# Create your views here.

def test(request):
    context = {"something": "hola jinja"}
    return render(request, "etiquetado_auto/test.html", context)
