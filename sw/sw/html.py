from django.shortcuts import render


def collection_list(request):
    return render(request, "collections.html")


def collection_details(request, pk):
    return render(request, "collection_details.html")


def collection_count(request, pk):
    return render(request, "count.html")
