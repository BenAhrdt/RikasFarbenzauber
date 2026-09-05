from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from .access import administrator, FIELDS, capabilities
from .admin_forms import AccountForm
from .models import UserAccess, Project, Photo

@administrator
def home(request):
    return render(request,'management/home.html',{'users_count':User.objects.count(),
        'projects_count':Project.objects.count(),'photos_count':Photo.objects.count()})

@administrator
def users(request):
    return render(request,'management/users.html',{'accounts':User.objects.annotate(project_count=Count('project')).order_by('username')})

@administrator
@require_http_methods(['GET','POST'])
def account(request,pk=None):
    user=get_object_or_404(User,pk=pk) if pk else User(is_active=True)
    initial=capabilities(user) if pk else {key:True for key in FIELDS}
    form=AccountForm(request.POST or None,instance=user,initial=initial)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            User.objects.filter(pk=request.user.pk).update(last_login=F('last_login'))
            if pk==request.user.pk and (not form.cleaned_data['is_active'] or not form.cleaned_data['is_superuser']):
                form.add_error(None,'Dein eigenes Administratorkonto muss aktiv und Administrator bleiben.')
            elif pk and User.objects.filter(pk=pk,is_active=True,is_superuser=True).exists() and (not form.cleaned_data['is_active'] or not form.cleaned_data['is_superuser']) and not User.objects.filter(is_active=True,is_superuser=True).exclude(pk=pk).exists():
                form.add_error(None,'Mindestens ein aktiver Administrator muss erhalten bleiben.')
            else:
                user=form.save(commit=False)
                user.is_staff=user.is_superuser
                if form.cleaned_data['password1']:user.set_password(form.cleaned_data['password1'])
                user.save()
                UserAccess.objects.update_or_create(user=user,defaults={key:form.cleaned_data[key] for key in FIELDS})
                if user.pk==request.user.pk and form.cleaned_data['password1']:update_session_auth_hash(request,user)
                messages.success(request,'Benutzer und Rechte wurden gespeichert.')
                return redirect('manage_users')
    return render(request,'management/account.html',{'form':form,'editing':bool(pk),'account':user})
