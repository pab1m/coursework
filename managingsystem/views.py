import json

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404

from .models import Appliance, PowerCalculation


@login_required(login_url="login")
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    appliances = Appliance.objects.filter(user=request.user)
    return render(request, 'managingsystem/index.html',{
        "appliances": appliances
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "managingsystem/login.html", {
                "message": "Invalid"
            })

    return render(request, "managingsystem/login.html")


def logout_view(request):
    logout(request)
    return render(request, "managingsystem/login.html")


def sign_up(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "managingsystem/signup.html")

        user = User.objects.create_user(username=username, password=password)
        user.save()
        login(request, user)
        return redirect("index")
    return render(request, "managingsystem/signup.html")


def add_app(request):
    if request.method == 'POST':
        brand_name = request.POST.get('brand_name')
        product_name = request.POST.get('product_name')
        power = request.POST.get('power')
        status = request.POST.get('status')

        if brand_name and product_name and power and status:
            try:
                power = float(power)  # Перетворення на float
                appliance = Appliance.objects.create(
                    user=request.user,
                    brand_name=brand_name,
                    product_name=product_name,
                    power=power,
                    status=status
                )
                messages.success(request, 'Appliance added successfully!')
                return redirect("index")
            except ValueError:
                messages.error(request, 'Invalid power value. Please enter a valid number.')
        else:
            messages.error(request, 'All fields are required.')

    appliances = Appliance.objects.filter(user=request.user)
    return render(request, "managingsystem/index.html", {
        'appliances': appliances
    })


def delete_app(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id, user=request.user)
    appliance.delete()
    return redirect("index")


def update_app(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id, user=request.user)
    if request.method == 'POST':
        brand_name = request.POST.get('brand_name')
        product_name = request.POST.get('product_name')
        power = request.POST.get('power')
        status = request.POST.get('status')

        # Перевірка заповненості полів
        if not (brand_name and product_name and power and status):
            messages.error(request, 'Усі поля повинні бути заповнені.')
            return redirect('index')

        appliance.brand_name = brand_name
        appliance.product_name = product_name
        appliance.power = power
        appliance.status = status
        appliance.save()
        messages.success(request, 'Прилад успішно оновлено!')
        return redirect("index")
    return render(request, 'managingsystem/index.html', {'appliance': appliance})


def toggle_status(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id, user=request.user)
    if appliance.status == 'Ввімкнений':
        appliance.status = 'Вимкнений'
    else:
        appliance.status = 'Ввімкнений'
    appliance.save()
    return redirect("index")


def power_calculation(request):
    if request.method == "POST":
        brand_name = request.POST.get('brand_name')
        product_name = request.POST.get('product_name')
        quantity = request.POST.get('quantity')

        if brand_name and product_name and quantity:
            try:
                quantity = int(quantity)
                appliance = Appliance.objects.filter(user=request.user,
                                                     brand_name=brand_name,
                                                     product_name=product_name,
                                                     status='Ввімкнений').first()

                if appliance:
                    PowerCalculation.objects.create(
                        user=request.user,
                        brand_name=brand_name,
                        product_name=product_name,
                        power=appliance.power,
                        quantity=quantity
                    )
                    messages.success(request, 'Item added successfully!')
                else:
                    messages.error(request, 'Appliance not found.')

            except ValueError:
                messages.error(request, 'Invalid quantity value. Please enter a valid number.')

        else:
            messages.error(request, 'All fields are required.')

        return redirect('power_calculation')

    appliances = Appliance.objects.filter(user=request.user, status='Ввімкнений')
    items = PowerCalculation.objects.filter(user=request.user)
    total_power = sum(item.power * item.quantity for item in items)

    brands = appliances.values_list('brand_name', flat=True).distinct()
    appliances_json = json.dumps(list(appliances.values('brand_name', 'product_name')))

    return render(request, 'managingsystem/powercalculation.html', {
        'appliances': appliances,
        'items': items,
        'total_power': total_power,
        'brands': brands,
        'appliances_json': appliances_json,
    })


def dashboard(request):
    return render(request, 'managingsystem/dashboard.html')