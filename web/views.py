from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


# Create your views here.

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
                # messages.info(request, 'Login yoki parolda xatolik!')
                login(request, user)
                return redirect('table')

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