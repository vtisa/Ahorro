from pyexpat.errors import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Cuenta, Transaccion
from decimal import Decimal
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.contrib.auth import logout
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cuenta.objects.create(usuario=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registro.html', {'form': form})


def cerrar_sesion(request):
    logout(request)
    return redirect('dashboard')

@login_required
def dashboard(request):
    cuenta = Cuenta.objects.get(usuario=request.user)
    transacciones = Transaccion.objects.filter(cuenta=cuenta).order_by('-fecha')
    
    total_ahorros = sum(t.monto for t in transacciones if t.tipo == 'ahorro')
    max_saldo = max(cuenta.saldo + total_ahorros, 1000)  

    porcentaje_saldo = (cuenta.saldo / max_saldo) * 100
    porcentaje_ahorro = (total_ahorros / max_saldo) * 100

    context = {
        'cuenta': cuenta,
        'transacciones': transacciones,
        'total_ahorros': total_ahorros,
        'porcentaje_saldo': porcentaje_saldo,
        'porcentaje_ahorro': porcentaje_ahorro,
        'max_saldo': max_saldo,
    }
    return render(request, 'dashboard.html', context)

@login_required
def realizar_transaccion(request):
    if request.method == 'POST':
        cuenta = Cuenta.objects.get(usuario=request.user)
        tipo = request.POST.get('tipo')
        monto = Decimal(request.POST.get('monto'))
        nota = request.POST.get('nota')

        if tipo == 'ingreso':
            cuenta.saldo += monto
            messages.success(request, 'Ingreso realizado con éxito.')
        elif tipo == 'gasto':
            if cuenta.saldo >= monto:
                cuenta.saldo -= monto
                messages.success(request, 'Gasto realizado con éxito.')
            else:
                messages.error(request, 'Saldo insuficiente para realizar este gasto.')
                return redirect('dashboard')
        elif tipo == 'ahorro':
            if cuenta.saldo >= monto:
                cuenta.saldo -= monto
                messages.success(request, 'Ahorro realizado con éxito.')
            else:
                messages.error(request, 'Saldo insuficiente para realizar este ahorro.')
                return redirect('dashboard')

        cuenta.save()
        Transaccion.objects.create(cuenta=cuenta, tipo=tipo, monto=monto, nota=nota)

    return redirect('dashboard')

@login_required
def generar_pdf(request):
    cuenta = Cuenta.objects.get(usuario=request.user)
    transacciones = Transaccion.objects.filter(cuenta=cuenta).order_by('-fecha')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    data = [['Fecha', 'Tipo', 'Monto', 'Nota']]
    for trans in transacciones:
        data.append([
            trans.fecha.strftime('%d/%m/%Y %H:%M'),
            trans.tipo,
            f"s/. {trans.monto:.2f}",
            trans.nota
        ])

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('TEXTCOLOR',(0,1),(-1,-1),colors.black),
        ('ALIGN',(0,1),(-1,-1),'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 12),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ])
    table.setStyle(style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='historial_transacciones.pdf')