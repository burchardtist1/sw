from django.shortcuts import redirect, render, resolve_url


def index(request):
    return redirect(resolve_url("html-collections"))


def collection_list(request):
    return render(request, "collections.html")


def collection_details(request, pk):
    return render(request, "collection_details.html")


def collection_count(request, pk):
    return render(request, "count.html")
