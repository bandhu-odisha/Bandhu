from django.shortcuts import render

# Create your views here.

def ashram(request):
    return render(request, 'ashram/index.html')
