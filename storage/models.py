from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Client(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    last_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Фамилия'
    )
    first_name = models.CharField(
        max_length=200,
        null=True,
        blank=False,
        verbose_name='Имя'
    )
    middle_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name='Отчество'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    phonenumber = models.CharField(
        'Номер телефона',
        max_length=20
    )
    is_admin = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        verbose_name='Администратор'
    )


    def __str__(self):
        return f'{self.id} {self.last_name} {self.first_name} {self.middle_name}'


class Order(models.Model):
    id = models.IntegerField(
        primary_key=True,
        unique=True,
        verbose_name='Номер заказа')
    date = models.DateField(
        null=False,
        default=timezone.now,
        verbose_name='Дата заказа')
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь')
    sum = models.FloatField(
        null=False,
        default=0,
        verbose_name='Стоимость')
    storage_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата начала')
    storage_to = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата окончания')

    def __str__(self):
        return f'{self.id} {self.date}'


class Warehouse(models.Model):
    id = models.IntegerField(
        primary_key=True,
        unique=True,
        verbose_name='Номер склада')
    address = models.CharField(
        max_length=200,
        verbose_name='Адрес')


class Box(models.Model):
    id = models.IntegerField(
        primary_key=True,
        unique=True,
        verbose_name='Номер ячейки')
    price = models.FloatField(
        null=False,
        default=0,
        verbose_name='Стоимость')
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='boxes',
        verbose_name='Склад')