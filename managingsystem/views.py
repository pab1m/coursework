import json
import pandas as pd

from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg, Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Appliance, PowerCalculation, PowerConsumption


@login_required(login_url="login")
def index(request):
    appliances = Appliance.objects.filter(user=request.user)
    return render(request, 'managingsystem/addappliance.html', {
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
                "message": "Некоректні дані"
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
            return render(request, "managingsystem/signup.html", {
                "message": "Паролі не співпадають"
            })

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
                return redirect("add_appliance")
            except ValueError:
                messages.error(request, 'Недійсне значення потужності. Введіть дійсний номер.')
        else:
            messages.error(request, 'All fields are required.')

    appliances = Appliance.objects.filter(user=request.user)
    return render(request, "managingsystem/addappliance.html", {
        'appliances': appliances
    })


def delete_app(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id, user=request.user)
    appliance.delete()
    return redirect("add_appliance")


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
            return redirect('add_appliance')

        appliance.brand_name = brand_name
        appliance.product_name = product_name
        appliance.power = power
        appliance.status = status
        appliance.save()
        messages.success(request, 'Прилад успішно оновлено!')
        return redirect("add_appliance")
    return render(request, 'managingsystem/addappliance.html', {'appliance': appliance})


def toggle_status(request, appliance_id):
    appliance = get_object_or_404(Appliance, id=appliance_id, user=request.user)
    if appliance.status == 'Ввімкнений':
        appliance.status = 'Вимкнений'
    else:
        appliance.status = 'Ввімкнений'
    appliance.save()
    return redirect("add_appliance")


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


def add_to_dashboard(request):
    if request.method == "POST":
        total_power = request.POST.get('total_power')

        if total_power:
            try:
                total_power = float(total_power)

                # Отримуємо поточну дату без часу
                today = timezone.now().date()

                # Перевіряємо, чи вже є запис для цього користувача за сьогоднішній день
                existing_record = PowerConsumption.objects.filter(user=request.user,
                                                                  date=today).first()

                if existing_record:
                    # Якщо такий запис є, додаємо нове значення до поточного
                    existing_record.total_power += total_power
                    existing_record.save()
                    messages.success(request, 'Total power updated on dashboard successfully!')
                else:
                    # Якщо запису немає, створюємо новий
                    PowerConsumption.objects.create(
                        user=request.user,
                        total_power=total_power
                    )
                    messages.success(request, 'Total power added to dashboard successfully!')

                # Видаляємо записи з PowerCalculation для поточного користувача
                records_to_delete = PowerCalculation.objects.filter(user=request.user)
                records_to_delete.delete()
                messages.success(request, 'Selected power calculations removed successfully!')

            except ValueError:
                messages.error(request, 'Invalid total power value.')

        return redirect('power_calculation')  # Повертаємось на сторінку обчислення потужності


def dashboard(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    power_consumptions = PowerConsumption.objects.filter(user=request.user).order_by('date')
    dates = [consumption.date.strftime('%Y-%m-%d') for consumption in power_consumptions]
    total_powers = [consumption.total_power for consumption in power_consumptions]

    return render(request, 'managingsystem/index.html', {
        'dates': dates,
        'total_powers': total_powers,
        'total_devices': power_consumptions.count(),
        'average_consumption': round(sum(total_powers) / len(total_powers) if total_powers else 0, 2),
        'total_consumption': sum(total_powers)
    })


def export_to_excel(request):
    # Отримуємо дані з бази даних
    data = PowerConsumption.objects.all().values('date', 'total_power')
    df = pd.DataFrame(list(data))

    # Додаємо статистику
    total_devices = PowerConsumption.objects.count()
    average_consumption = PowerConsumption.objects.aggregate(Avg('total_power'))['total_power__avg']
    total_consumption = PowerConsumption.objects.aggregate(Sum('total_power'))['total_power__sum']

    # Створюємо новий DataFrame для статистики
    stats_data = {
        'Показник': ['Кількість записів', 'Середнє споживання', 'Загальне споживання'],
        'Значення': [total_devices, average_consumption, total_consumption]
    }
    stats_df = pd.DataFrame(stats_data)

    # Створюємо Excel writer і записуємо дані на окремі листи
    with pd.ExcelWriter('report.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Дані')
        stats_df.to_excel(writer, index=False, sheet_name='Статистика')

    # Читаємо згенерований файл і відправляємо його як відповідь
    with open('report.xlsx', 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="report.xlsx"'
        return response
