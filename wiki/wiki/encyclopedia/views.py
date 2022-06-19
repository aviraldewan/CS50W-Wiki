from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from markdown2 import Markdown
from . import util
from random import randint

markdowner = Markdown()

class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={
        "class": "search",
        "placeholder": "Search Wikipedia"}))

class NewPageForm(forms.Form):
    title = forms.CharField(label='')
    content = forms.CharField(label = '', widget = forms.Textarea(attrs={
            "class": "content",
            "placeholder": "Enter Data(in Markdown)"}))

class EditForm(forms.Form):
    content = forms.CharField(label='', widget=forms.Textarea(attrs={
        "class": "content",
        "placeholder": "Enter Data(in Markdown)"}))

def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })


@csrf_exempt
def search(request):

    if request.method == "POST":
        data = SearchForm(request.POST)

        if data.is_valid():
            file = data.cleaned_data["query"]
            title = util.get_entry(file)
            if title:
                return HttpResponseRedirect(reverse('entry', args=[file]))
            else:
                related = []
                for entry_name in util.list_entries():
                    if file.lower() in entry_name.lower() or entry_name.lower() in file.lower():
                        related.append(entry_name)
                return render(request, "encyclopedia/search.html",{
                    "title": file,
                    "related_titles": related,
                    "searchform": SearchForm()
                })

    return HttpResponseRedirect(reverse('index'))

def entry(request,name):
    entry = util.get_entry(name)
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "message": "No Search Results Found!"
        })

    page_converted = markdowner.convert(entry)
    return render(request, "encyclopedia/entry.html", {
        "name": name,
        "content": page_converted
    })

def random(request):
    all_entries = util.list_entries()
    random_page = randint(0,len(all_entries)-1)
    page = util.get_entry(all_entries[random_page])
    page_converted = markdowner.convert(page)

    return render(request, "encyclopedia/entry.html", {
        "name": all_entries[random_page],
        "content": page_converted
    })


@csrf_exempt
def newpage(request):

    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            entries = util.list_entries()
            if title in entries:
                return render(request, "encyclopedia/error.html", {
                    "form": SearchForm(),
                    "message": "Page already existed!"
                })
            else:
                util.save_entry(title,content)
                page = util.get_entry(title)
                page_converted = markdowner.convert(page)

                return render(request,"encyclopedia/entry.html",{
                    "form": SearchForm(),
                    "content": page_converted,
                    "name": title
                })

    return render(request, "encyclopedia/newpage.html", {
        "form": SearchForm(),
        "post": NewPageForm()
    })


@csrf_exempt
def edit(request,name):

    if request.method == "GET":
        page = util.get_entry(name)

        return render(request, "encyclopedia/edit.html",{
            "form": SearchForm(),
            "name": name,
            "edit": EditForm(initial={'content':page})
        })
    else:
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(name,content)
            page = util.get_entry(name)
            page_converted = markdowner.convert(page)

            return render(request,"encyclopedia/entry.html",{
                "form": SearchForm(),
                "content": page_converted,
                "name": name
            })