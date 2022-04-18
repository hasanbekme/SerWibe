from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


# Create your views here.


def logoutUser(request):
    logout(request)
    return redirect('signin')


def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if (user is not None) and username == "admin":
                login(request, user)
                return redirect('dashboard')
            elif user is not None:
                login(request, user)
                return redirect('room')

        context = {}
        return render(request, 'login.html', context)


#@login_required(login_url='/')
def dashboard(request):
    return render(request, 'dashboard.html')


#@login_required(login_url='/')
def income(request):
    return render(request, 'income.html')


#@login_required(login_url='/')
def worker(request):
    return render(request, 'worker.html')


#@login_required(login_url='/')
def product(request):
    return render(request, 'product.html')


#@login_required(login_url='/')
def category(request):
    return render(request, 'category.html')


#@login_required(login_url='/')
def table(request):
    return render(request, 'table.html')


#@login_required(login_url='/')
def order(request):
    return render(request, 'order.html')


#@login_required(login_url='/')
def document(request):
    return render(request, 'document.html')