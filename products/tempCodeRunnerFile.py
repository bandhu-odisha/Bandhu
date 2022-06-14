return render(request, 'products.html', {
            "data": query_set,
            "content": HomePage.objects.all().first()
        })