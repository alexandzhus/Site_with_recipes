from django.shortcuts import render

from django.http import HttpRequest, HttpResponse

def test_index_page(request:HttpRequest) -> HttpResponse:
    return render(request, 'recipes/index.html')
