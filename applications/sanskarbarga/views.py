from django.shortcuts import render

# Create your views here.

def sanskarbarga(request):
    return render(request, 'sanskarbarga/index.html')
