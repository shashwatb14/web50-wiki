from django.shortcuts import render
from django import forms
from . import util
from markdown2 import Markdown

markdowner = Markdown()

class NewEntryForm(forms.Form):
    title = forms.CharField(label="New title")
    markdown_content = forms.CharField(widget=forms.Textarea)

def index(request):
    if request.method == "POST":
        if request.POST['q']:
            return search(request, False)

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if request.method == "POST":
        try:
            if request.POST['q']:
                return search(request, True)
        except:
            pass

    entry = util.get_entry(title)
    content, title = "", "Error 404"

    if entry:
        content = markdowner.convert(entry)
        title = content.split("<h1>")[1].split("</h1>")[0]
    
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": entry,
        "content": content
    })


def new(request):
    if request.method == "POST":
        try:
            if request.POST['q']:
                return search(request, False)
        except:
            pass

        form = NewEntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["markdown_content"]
            print(title, content)
        
        if not util.get_entry(title):
            with open(f"entries/{title}.md", "w") as f:
                f.write(f"# {title}\n")
                f.write(content)

            return entry(request, title)
        
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form,
                "error": True
            })

    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })


def search(request, is_entry):
    query = request.POST['q']
    full_query = query in [i.lower() for i in util.list_entries()]

    if full_query and not is_entry:
        return entry(request, query)
    
    elif full_query and is_entry:
        data = util.get_entry(query)
        content = markdowner.convert(data)
        title = content.split("<h1>")[1].split("</h1>")[0]
    
        return render(request, "encyclopedia/entry.html", {
            "entry": data,
            "title": title,
            "content": content
        })
    
    entries = []
    for item in util.list_entries():
        if request.POST['q'] in item.lower():
            entries.append(item)

    print(entries)
    return render(request, "encyclopedia/search.html", {
        "entries": entries,
        "from_entry": is_entry
    })