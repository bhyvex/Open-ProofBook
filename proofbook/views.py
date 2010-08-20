# -*- coding: utf-8 -*-
# Create your views here.
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render_to_response
from open_proofbook.proofbook.models import Album
from open_proofbook.proofbook.forms import CreateAlbumForm
import os

def home(request):
  public_albums = Album.objects.filter(public=True)
  
  return HttpResponse("Home")

def create_album(request):
  staff_only(request)
  #if request.method == 'GET':
   # render_to_response(create_album.html)
  
  if request.method == 'POST':
    pass
  else:
    form = CreateAlbumForm()
    return render_to_response('form.html',{'form': form})
      
def album(request, album, curr_page=1):
  owner_only(request, album)
  try:
    a = Album.objects.get(path=album)
  except Album.DoesNotExist:
    return HttpResponseNotFound()
  album_path = settings.STATIC_DOC_ROOT + '/albums/' + album
  
  #Get all the pictures in the album directory.  Need to add filters for 
  #directories and non-picture files.
  pic_list = sorted(os.listdir(album_path))
  
  #Find indices of pictures to show based on page.
  page = int(curr_page)
	  
  if page < 1:
    return HttpResponseNotFound()
    
  pic_pages = int(settings.PICS_PER_PAGE)
  if pic_pages == 0:
    raise ZeroDivisionError
  #Integer division should show many pages are possible, given the num of pics
  avail_pages = ((len(pic_list)) / pic_pages) + 1
  
  if page < avail_pages:
    pic_max = (page * 9) - 1
    pic_min = pic_max - 8
  elif page == avail_pages:
    pic_min = (page - 1) * 9
    remainder = (len(pic_list) - 1) % pic_pages
    pic_max = pic_min + remainder
  else:
    return HttpResponseNotFound()
    
  #Fill list with numbers of pages
  page_list = range(1, avail_pages + 1)
  print len(page_list)
  #Prepare template payload
  if request.user.is_authenticated():
    name = request.user.first_name + ' ' + request.user.last_name
  else:
    name = "Anonymous!"
    
  # Find next and previous links, checking if there even is a next/prev page
  if page < avail_pages:
    next_page = '/' + album + '/' + str(page + 1)
  else:
    next_page = None
  if page > 1:
    prev_page = '/' + album + '/' + str(page - 1)
  else:
    prev_page = None
  
  
  if settings.DEBUG:
    print 'Page: ' + str(page) + ' picmin: ' + str(pic_min) + ' picmax: ' + str(pic_max) + ' picpages: ' + str(pic_pages) + ' avail: ' + str(avail_pages) + ' pic_list len ' + str(len(pic_list))
    print pic_list[0]
    
  payload = {
    'title': a.title,
    'page': page,
    'next_page': next_page,
    'prev_page': prev_page,
    'user': name,
    'public': a.public,
    'pic_list': pic_list[pic_min:pic_max],
    'page_list': page_list,
    'path': album,
    'album_dir': '/static/albums/' + album + '/',
    }
  return render_to_response('album.html', payload)

def album_edit(request, album):
  staff_only(request)
  
#Aux

def staff_only(request):
  if (request.user.is_authenticated() == False):
    return HttpResponseRedirect('/accounts/login')
  if (request.user.is_staff == False & user.is_athenticated()):
    return HttpResponseForbidden()
def owner_only(request, album):
  if (request.user.is_authenticated() == False):
    return HttpResponseRedirect('/accounts/login')
  try:
    a = Album.objects.get(path=album)
  except Album.DoesNotExist:
    return HttpResponseNotFound()
  if (a.public == False &  request.user.is_staff == False): #a.owner != request.user <- Should work! Both should be a User object
    return HttpResponseForbidden()
    
