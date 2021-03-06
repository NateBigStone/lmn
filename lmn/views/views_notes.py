from django.shortcuts import render, redirect, get_object_or_404

from ..models import Venue, Artist, Note, Show
from ..forms import VenueSearchForm, NewNoteForm, NoteSearchForm, UserRegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core.paginator import Paginator


@login_required
def new_note(request, show_pk):

    show = get_object_or_404(Show, pk=show_pk)

    if request.method == 'POST' :
        form = NewNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.show = show
            note.save()
            return redirect('note_detail', note_pk=note.pk)

    else :
        form = NewNoteForm()

    return render(request, 'lmn/notes/new_note.html', { 'form': form, 'show': show })


def latest_notes(request):
    notes = Note.objects.all().order_by('-posted_date')
        
    paginator = Paginator(notes, 25)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    
    return render(request, 'lmn/notes/note_list.html', { 'notes': page_object })


def notes_for_show(request, show_pk): 
    """Notes for show, most recent first"""
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date')
    show = Show.objects.get(pk=show_pk)  
    
    paginator = Paginator(notes, 25)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
    
    return render(request, 'lmn/notes/note_list.html', {'show': show, 'notes': page_object})


def note_detail(request, note_pk):
    """Specific details of a note"""
    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html', {'note': note})

def best_shows(request):
    notes = Note.objects.all().order_by('-rating')
    return render(request, 'lmn/best_shows/best_shows.html', { 'notes': notes })

@login_required
def user_notes(request):
    """User can see their own notes"""
    form = NoteSearchForm()
    search_name = request.GET.get('search_name')
    if search_name:
        notes = Note.objects.filter(user=request.user, title__icontains=search_name).order_by('-posted_date') | \
                Note.objects.filter(user=request.user, text__icontains=search_name).order_by('-posted_date')
    else:
        notes = Note.objects.filter(user=request.user).order_by('-posted_date')
    paginator = Paginator(notes, 25)
    page_number = request.GET.get('page')
    page_object = paginator.get_page(page_number)
        
    return render(request, 'lmn/notes/note_list.html', {'notes': page_object, 'my_notes': True, 'form': form,
                                                        'search_term': search_name})

