from django.shortcuts import render
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from cms_put.models import *


# Create your views here.
@csrf_exempt  #SE UTILIZA PARA QUE NOS PERMITA REALIZAR EL POST
def main(request):
    if request.method == 'GET':
        htmlAnswer = "<form id='paginas' method='POST'>" \
            + "<label> Introduce el recurso y el contenido del recurso" \
            + "</br></label>" \
            + "<input name='name' type='text'>" \
            + "<br>" \
            + "<textarea name='page' rows='20' cols='100' ></textarea>" \
            + "<br>" \
            + "<input type='submit' value='Enviar'></form>"
        return HttpResponse(htmlAnswer)
    elif request.method == 'PUT':
        return HttpResponseNotFound("Bad Request")
    elif request.method == 'POST':
        recurso = request.POST['name']
        contenido = request.POST['page']
        pagina = Pages(name=recurso, page=contenido)
        pagina.save()
        return HttpResponse("Hacemos un POST en /" + recurso)

@csrf_exempt
def recurso(request, nombreRecurso):
    if request.method == 'GET':
        try:
            pagina = Pages.objects.get(name=nombreRecurso)
            return HttpResponse(pagina.page)
        except Pages.DoesNotExist:
            return HttpResponseNotFound("Page Not Found!<br>/" + nombreRecurso \
                    + " No existe tal recurso")
    elif request.method == 'POST':
        htmlAnswer = "<!DOCTYPE html><html><body>" \
                    + "Para crear una pagina vaya, haga click " \
                    + "<a href='localhost:1231/'> aqui</a>" \
                    + "</body></html>"
        HttpResponseNotFound(htmlAnswer)
    elif request.method == 'PUT':
        try:
            pagina = Pages.objects.get(name=nombreRecurso)
            pagina.page = request.body.decode('utf-8')
            pagina.save()
            return(HttpResponse("Se ha actualizado /" + nombreRecurso))
        except Pages.DoesNotExist:
            return HttpResponseNotFound("ERROR! Realizando un PUT sobre algo inexistente")
