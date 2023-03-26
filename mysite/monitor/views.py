from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView
from .models import Host, Time
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from .form import HostForm, TimeForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .decorator import allowed_users


@login_required(login_url="/login")
def index(request):
    return render(request, template_name='monitor/index.html')


class HostView(LoginRequiredMixin, ListView):

        login_url = '/login'
        template_name = 'monitor/host.html'
        context_object_name = 'host_list'
        context_object_name = 'time_list'

        def get_queryset(self):
            return Host.objects.all().order_by('-status', '-last_status_change')

        def get_queryset(self):
            return Time.objects.all().order_by('set_hours')


@allowed_users(allowed_roles=['admin'])
def host_list(request):
    host_list = Host.objects.all()
    p = Paginator(Host.objects.order_by('-status', '-last_status_change'), 10)
    page = request.GET.get('page')
    hosts = p.get_page(page)
    nums = "a" * hosts.paginator.num_pages
    return render(request, 'monitor/host_list.html', {'host_list': host_list, 'hosts': hosts, 'nums': nums})


class FullViewHost(LoginRequiredMixin, ListView):
    login_url = '/login'
    template_name = 'monitor/fullviewhost.html'
    context_object_name = 'host_list'

    def get_queryset(self):
        return Host.objects.all().order_by('-status', '-last_status_change')


class HostDetailView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name = 'monitor/host_detail.html'

    def get_context_data(self, **kwargs):
        host = Host.objects.get(id=self.kwargs['pk'])
        context = super(HostDetailView, self).get_context_data(**kwargs)
        context['host'] = host
        return context


def user_login(request):
    if request.user.is_authenticated:
        return render(request, 'monitor/index.html')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'monitor/index.html')
            else:
                messages.error(request, "Username hoặc Mật khẩu không đúng. Vui lòng đăng nhập lại!")
        return render(request, 'monitor/login.html')


@login_required(login_url="/login")
def user_logout(request):
    logout(request)
    messages.warning(request, "Bạn đã đăng xuất. Vui lòng đăng nhập lại!")
    return redirect('/login')


@login_required(login_url="/login")
def contact(request):
    return render(request, template_name='monitor/contact.html')


@login_required(login_url="/login")
@allowed_users(allowed_roles=['admin'])
def reload(request):
    for host in Host.objects.all():
        host.check_and_update()
    return render(request, 'monitor/host.html')


@login_required(login_url="/login")
@allowed_users(allowed_roles=['admin'])
def reload_host(request, host_id):
    for hosts in Host.objects.filter(pk=host_id):
        hosts.check_and_update()
    return render(request, 'monitor/host.html')


@login_required(login_url="/login")
@allowed_users(allowed_roles=['admin'])
def add_host(request):
    submitted = False
    if request.method == "POST":
        form = HostForm(request.POST)
        if form.is_valid() and request.user.has_perm('monitor.add_host'):
            form.save()
            return HttpResponseRedirect('/addhost?submitted=True')
        else:
            return HttpResponseRedirect('/addhost?submitted=False')
    else:
        form = HostForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'monitor/addhost.html', {'form': form, 'submitted': submitted})


@login_required(login_url="/login")
def search_host(request):
    if request.method == "POST":
        search = request.POST['search']
        hosts = Host.objects.filter(Q(address__icontains=search) | Q(name__icontains=search)).order_by('-status', '-last_status_change')
        return render(request, 'monitor/search.html', {'search': search, 'hosts': hosts})
    else:
        return render(request, 'monitor/search.html', {})


@login_required(login_url="/login")
def search_fullview_host(request):
    if request.method == "POST":
        search = request.POST['search']
        hosts = Host.objects.filter(Q(address__icontains=search) | Q(name__icontains=search)).order_by('-status', '-last_status_change')
        return render(request, 'monitor/searchfullview.html', {'search': search, 'hosts': hosts})
    else:
        return render(request, 'monitor/searchfullview.html', {})


@login_required(login_url="/login")
@allowed_users(allowed_roles=['admin'])
def update_host(request, host_id):
    host = Host.objects.get(pk=host_id)
    form = HostForm(request.POST or None, instance=host)
    if form.is_valid() and request.method == "POST":
        form.save()
        return HttpResponseRedirect('/host')
    return render(request, 'monitor/update_host.html', {'host': host, 'form': form})


@login_required(login_url="/login")
@allowed_users(allowed_roles=['admin'])
def delete_host(request, host_id):
    host = Host.objects.get(pk=host_id)
    if request.method == "POST":
        host.delete()
        return HttpResponseRedirect('/host')
    return render(request, 'monitor/delete.html', {'name': host, 'address': host})


@login_required(login_url="/login")
@allowed_users(allowed_roles=['admin'])
def set_time(request, time_id):
    time = Time.objects.get(pk=time_id)
    form = TimeForm(request.POST or None, instance=time)
    if form.is_valid() and request.method == "POST":
        form.save()
        return HttpResponseRedirect('/host')
    return render(request, 'monitor/set_time.html', {'set_time': time, 'form': form})
