from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
# Create your views here.
from .models import Post
from .forms import PostForm
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form=PostForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.user=request.user
        instance.save()
        messages.success(request,"Post Created Successfully!!")
        return HttpResponseRedirect(instance.get_absolute_url())
        

    context={
        "form":form
    }
    return render(request,"post_form.html",context)

def post_detail(request,slug=None):
    obj=get_object_or_404(Post,slug=slug)
    if  obj.publish > timezone.now().date() or obj.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404

    context={
        "title":obj.title,
        "obj":obj
    }
    return render(request,"post_detail.html",context)
    

def post_list(request):
    today=timezone.now().date()
    queryset_list=Post.objects.active()
    if request.user.is_staff or request.user.is_superuser:
        queryset_list=Post.objects.all()

    query=request.GET.get("q")
    if query:
        queryset_list=queryset_list.filter(
                            Q(title__icontains=query) |
                            Q(content__icontains=query) |
                            Q(user__first_name__icontains=query) |
                            Q(user__last_name__icontains=query)
                            )
    paginator=Paginator(queryset_list,5)
    page_request_var="page"
    page=request.GET.get(page_request_var)
    try:
        queryset=paginator.page(page)
    except PageNotAnInteger:
        queryset=paginator.page(1)
    except EmptyPage:
        queryset=paginator.page(paginator.num_pages)
    context={
    		"title":"List",
            "object_list":queryset,
            "page_request_var":page_request_var,
            "today":today
    	}

    return render(request,"post_list.html",context)

def post_update(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    
    instance=get_object_or_404(Post,slug=slug)
    form=PostForm(request.POST or None,request.FILES or None,instance=instance)
    if form.is_valid():
        instance=form.save(commit=False)
        instance.save()
        return HttpResponseRedirect(instance.get_absolute_url())
        messages.success(request,"Post Saved Successfully!!")
    context={
        "title":instance.title,
        "instance":instance,
        "form":form
    }
    return render(request,"post_form.html",context)

def post_delete(request,slug=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance=get_object_or_404(Post,slug=slug)
    instance.delete()
    messages.success(request,"Sucessfully Deleted")
    return redirect("list")
