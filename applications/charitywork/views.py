from django.shortcuts import render

# Create your views here.

def charity_work(request):
    return render(request, 'charitywork/index.html')
