from django.shortcuts import render

# Create your views here.

def signin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if (user is not None) and username=="admin":
                login(request, user)
                return redirect('dashboard')
            elif user is not None:
                #messages.info(request, 'Login yoki parolda xatolik!')
                login(request, user)
                return redirect('table')

        context={}
        return render(request, 'login.html', context)