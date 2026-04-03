from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def contacts(request):
    return render(request, 'contacts.html')

def calculator(request):
    return render(request, 'calculator.html')

def services(request):
    return render(request, 'services.html')
