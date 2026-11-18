from datetime import datetime, time, timedelta
from unittest.mock import patch
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import Categoria, DetallePedido, Pedido, Producto


class CafeteriaTests(TestCase):
    def setUp(self):
        self.encargado = User.objects.create_user(
            username='encargado',
            email='carlos@inacap.cl',
            password='inacap123',
            first_name='Carlos',
            is_staff=True,
            is_superuser=True,
        )
        self.cliente1 = User.objects.create_user(
            username='cliente1',
            email='ana@inacapmail.cl',
            password='inacap123',
            first_name='Ana',
            is_staff=False,
        )
        self.cliente2 = User.objects.create_user(
            username='cliente2',
            email='diego@inacapmail.cl',
            password='inacap123',
            first_name='Diego',
            is_staff=False,
        )

        self.cat_cafe = Categoria.objects.create(nombre='Cafetería', activa=True)
        self.cat_inactiva = Categoria.objects.create(nombre='Inactiva', activa=False)

        self.prod_ok = Producto.objects.create(
            categoria=self.cat_cafe,
            codigo='CAF-001',
            nombre='Espresso',
            precio=1500,
            stock=5,
            disponible=True,
        )
        self.prod_mucho_stock = Producto.objects.create(
            categoria=self.cat_cafe,
            codigo='CAF-002',
            nombre='Americano',
            precio=1700,
            stock=20,
            disponible=True,
        )
        self.prod_agotado = Producto.objects.create(
            categoria=self.cat_cafe,
            codigo='CAF-009',
            nombre='Churrasco',
            precio=3800,
            stock=0,
            disponible=True,
        )
        self.prod_no_disp = Producto.objects.create(
            categoria=self.cat_cafe,
            codigo='CAF-010',
            nombre='Vegetariano',
            precio=2900,
            stock=8,
            disponible=False,
        )
        self.prod_cat_inact = Producto.objects.create(
            categoria=self.cat_inactiva,
            codigo='CAF-021',
            nombre='Chocolate',
            precio=2200,
            stock=10,
            disponible=True,
        )

    def test_rf01_proteccion_eliminacion_y_restriccion_unica(self):
        with self.assertRaises(ProtectedError):
            self.cat_cafe.delete()

        pedido = Pedido.objects.create(
            cliente=self.cliente1,
            hora_retiro=time(12, 0),
            estado='Pendiente',
            total=1500,
        )
        DetallePedido.objects.create(
            pedido=pedido,
            producto=self.prod_ok,
            cantidad=1,
            precio_unitario=1500,
            subtotal=1500,
        )

        with self.assertRaises(ProtectedError):
            self.prod_ok.delete()

        with self.assertRaises(IntegrityError):
            DetallePedido.objects.create(
                pedido=pedido,
                producto=self.prod_ok,
                cantidad=2,
                precio_unitario=1500,
                subtotal=3000,
            )

    def test_rf02_autenticacion_y_control_roles(self):
        rutas_protegidas = [
            '/',
            '/catalogo/',
            '/carrito/',
            '/pedidos/',
            '/gestion/pedidos/',
            '/gestion/productos/',
            '/gestion/categorias/',
        ]
        for ruta in rutas_protegidas:
            resp = self.client.get(ruta)
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/login/', resp['Location'])

        self.client.login(username='cliente1', password='inacap123')
        for ruta in ['/gestion/', '/gestion/pedidos/', '/gestion/productos/', '/gestion/categorias/']:
            resp = self.client.get(ruta)
            self.assertEqual(resp.status_code, 403)

        resp_menu = self.client.get('/catalogo/')
        contenido = resp_menu.content.decode('utf-8')
        self.assertIn('Ana (cliente1)', contenido)
        self.assertIn('Cliente', contenido)

        self.client.logout()
        self.client.login(username='encargado', password='inacap123')
        for ruta in ['/catalogo/', '/carrito/', '/pedidos/']:
            resp = self.client.get(ruta)
            self.assertEqual(resp.status_code, 403)

        resp_enc = self.client.get('/gestion/productos/')
        contenido_enc = resp_enc.content.decode('utf-8')
        self.assertIn('Carlos (encargado)', contenido_enc)
        self.assertIn('Encargado', contenido_enc)

    def test_rf03_catalogo_clientes(self):
        self.client.login(username='cliente1', password='inacap123')
        resp = self.client.get('/catalogo/')
        html = resp.content.decode('utf-8')

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Espresso', html)
        self.assertIn('$1.500', html)
        self.assertIn('Churrasco', html)
        self.assertIn('Agotado', html)
        self.assertNotIn('Vegetariano', html)
        self.assertNotIn('Chocolate', html)

        resp_filtro = self.client.get('/catalogo/', {'q': 'Esp'})
        html_filtro = resp_filtro.content.decode('utf-8')
        self.assertIn('Espresso', html_filtro)
        self.assertNotIn('Americano', html_filtro)

    def test_rf04_gestion_catalogo_encargado(self):
        self.client.login(username='encargado', password='inacap123')

        resp_err = self.client.post('/gestion/productos/nuevo/', {
            'categoria': self.cat_cafe.pk,
            'codigo': 'ERR-1',
            'nombre': 'Invalido',
            'precio': 50,
            'stock': -2,
            'disponible': 'on',
        })
        self.assertEqual(resp_err.status_code, 200)
        self.assertFalse(Producto.objects.filter(nombre='Invalido').exists())
        err_html = resp_err.content.decode('utf-8')
        self.assertIn('CAF-000', err_html)
        self.assertIn('$100', err_html)
        self.assertIn('negativo', err_html)

        resp_ok = self.client.post('/gestion/productos/nuevo/', {
            'categoria': self.cat_cafe.pk,
            'codigo': 'CAF-050',
            'nombre': 'Cortado',
            'precio': 1800,
            'stock': 12,
            'disponible': 'on',
        }, follow=True)
        self.assertEqual(resp_ok.status_code, 200)
        self.assertTrue(Producto.objects.filter(codigo='CAF-050').exists())

        resp_del = self.client.post(f'/gestion/categorias/{self.cat_cafe.pk}/eliminar/', follow=True)
        self.assertEqual(resp_del.status_code, 200)
        self.assertTrue(Categoria.objects.filter(pk=self.cat_cafe.pk).exists())
        self.assertIn('productos asociados', resp_del.content.decode('utf-8'))

    def test_rf05_carrito_y_confirmacion_todo_o_nada(self):
        self.client.login(username='cliente1', password='inacap123')

        self.client.post(f'/carrito/agregar/{self.prod_agotado.pk}/')
        self.assertEqual(sum(self.client.session.get('carrito', {}).values()), 0)

        for _ in range(12):
            self.client.post(f'/carrito/agregar/{self.prod_mucho_stock.pk}/')
        self.assertEqual(sum(self.client.session['carrito'].values()), 10)

        self.client.post('/carrito/vaciar/')
        self.assertEqual(self.client.session.get('carrito', {}), {})

        self.client.post(f'/carrito/agregar/{self.prod_ok.pk}/')
        self.client.post(f'/carrito/actualizar/{self.prod_ok.pk}/', {'cantidad': 3})
        self.assertEqual(self.client.session['carrito'][str(self.prod_ok.pk)], 3)

        ahora_fijo = timezone.make_aware(datetime(2026, 11, 18, 10, 0, 0))
        with patch('cafeteria.forms.timezone.localtime', return_value=ahora_fijo):
            resp_hora_mal = self.client.post('/carrito/confirmar/', {'hora_retiro': '10:15'})
            self.assertEqual(resp_hora_mal.status_code, 200)
            self.assertEqual(Pedido.objects.count(), 0)

            self.prod_ok.stock = 2
            self.prod_ok.save()
            resp_sin_stock = self.client.post('/carrito/confirmar/', {'hora_retiro': '10:30'}, follow=True)
            self.assertEqual(Pedido.objects.count(), 0)
            self.assertIn('Espresso', resp_sin_stock.content.decode('utf-8'))

            self.prod_ok.stock = 5
            self.prod_ok.save()
            resp_conf = self.client.post('/carrito/confirmar/', {
                'hora_retiro': '10:30',
                'observacion': 'Sin azúcar',
            })
            self.assertEqual(resp_conf.status_code, 302)
            self.assertEqual(Pedido.objects.count(), 1)
            pedido = Pedido.objects.first()
            self.assertEqual(pedido.estado, 'Pendiente')
            self.assertEqual(pedido.total, 4500)
            self.assertEqual(pedido.detalles.first().precio_unitario, 1500)
            self.prod_ok.refresh_from_db()
            self.assertEqual(self.prod_ok.stock, 2)
            self.assertEqual(self.client.session.get('carrito', {}), {})

    def test_rf06_seguimiento_cancelacion_y_estados(self):
        pedido = Pedido.objects.create(
            cliente=self.cliente1,
            hora_retiro=time(14, 0),
            estado='Pendiente',
            total=3000,
        )
        DetallePedido.objects.create(
            pedido=pedido,
            producto=self.prod_ok,
            cantidad=2,
            precio_unitario=1500,
            subtotal=3000,
        )
        self.prod_ok.stock = 3
        self.prod_ok.save()

        self.client.login(username='cliente2', password='inacap123')
        self.assertEqual(self.client.get(f'/pedidos/{pedido.pk}/').status_code, 403)
        self.assertEqual(self.client.post(f'/pedidos/{pedido.pk}/cancelar/').status_code, 403)

        self.client.logout()
        self.client.login(username='encargado', password='inacap123')
        self.client.post(f'/gestion/pedidos/{pedido.pk}/avanzar/', {'nuevo_estado': 'Listo'})
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'Pendiente')

        for estado in ['En preparación', 'Listo', 'Entregado']:
            self.client.post(f'/gestion/pedidos/{pedido.pk}/avanzar/', {'nuevo_estado': estado})
            pedido.refresh_from_db()
            self.assertEqual(pedido.estado, estado)

        pedido2 = Pedido.objects.create(
            cliente=self.cliente1,
            hora_retiro=time(15, 0),
            estado='Pendiente',
            total=3000,
        )
        DetallePedido.objects.create(
            pedido=pedido2,
            producto=self.prod_ok,
            cantidad=2,
            precio_unitario=1500,
            subtotal=3000,
        )
        self.prod_ok.stock = 1
        self.prod_ok.save()

        self.client.logout()
        self.client.login(username='cliente1', password='inacap123')
        self.client.post(f'/pedidos/{pedido2.pk}/cancelar/')
        pedido2.refresh_from_db()
        self.prod_ok.refresh_from_db()
        self.assertEqual(pedido2.estado, 'Cancelado')
        self.assertEqual(self.prod_ok.stock, 3)
