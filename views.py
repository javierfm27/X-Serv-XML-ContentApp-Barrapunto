from django.shortcuts import render
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from cms_put.models import *
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import feedparser
import urllib

class BarraPunto(ContentHandler):

    bodyHTML = ""

    def __init__(self):
        self.inContent = 0
        self.titulares = False
        self.theContent = ""

    def startElement(self, name, attrs):
        if name == 'item':
            self.titulares = True
        elif self.titulares:
            if name == 'title':
                self.inContent = 1
            elif name == 'link':
                self.inContent = 1

    def endElement(self, name):
        if name == 'item':
            self.titulares = False
        elif self.titulares:
            if name == 'title':
                titulo = "<br> Titular: " + self.theContent + ".<br>"
                self.bodyHTML = self.bodyHTML + titulo
                self.inContent = 0
                self.theContent = ""
            elif name == 'link':
                enlace = "<a href=" + self.theContent + \
                        "> Enlace:" + self.theContent + "</a>.<br>"
                self.bodyHTML = self.bodyHTML + enlace
                self.inContent = 0
                self.theContent = ""

    def characters(self, chars):
        if self.inContent:
            self.theContent = self.theContent + chars

def printAll(request):
    listaPaginas = Pages.objects.all()
    html = "<ul>Lista de Paginas:"
    for pagina in listaPaginas:
        html += "<li>" + pagina.name + "</li>"
    html += "</ul>"
    return html
# Create your views here.
@csrf_exempt  #SE UTILIZA PARA QUE NOS PERMITA REALIZAR EL POST
def main(request):
    if request.method == 'GET':
        htmlAnswer = printAll(request)
        htmlAnswer += "<form id='paginas' method='POST'>" \
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

            BarraPuntoRSS = "http://barrapunto.com/index.rss"
            xmlData = urllib.request.urlopen(BarraPuntoRSS)
            xmlData = xmlData.read().decode("utf-8")
            BarraPuntoParse = make_parser()
            BarraPuntoHandler = BarraPunto()
            BarraPuntoParse.setContentHandler(BarraPuntoHandler)
            fichero = open("barrapunto.xml", "w")
            fichero.write(xmlData)
            fichero.close()
            xmlFile = open("barrapunto.xml","r")
            BarraPuntoParse.parse(xmlFile)
            pagina = Pages.objects.get(name=nombreRecurso)
            return HttpResponse(BarraPuntoHandler.bodyHTML + pagina.page)
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
