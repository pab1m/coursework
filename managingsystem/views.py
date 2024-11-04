from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "managingsystem/index.html")


def greed(request, name):
    return render(request, 'managingsystem/greet.html', {
        "name": name.capitalize(),
    })