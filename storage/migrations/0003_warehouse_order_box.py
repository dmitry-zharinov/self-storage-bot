# Generated by Django 4.0.5 on 2022-06-30 12:15

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0002_rename_user_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='Номер склада')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='Номер заказа')),
                ('date', models.DateField(default=django.utils.timezone.now, verbose_name='Дата заказа')),
                ('sum', models.FloatField(default=0, verbose_name='Стоимость')),
                ('storage_from', models.DateTimeField(blank=True, null=True, verbose_name='Дата начала')),
                ('storage_to', models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='storage.client', verbose_name='Пользователь')),
            ],
        ),
        migrations.CreateModel(
            name='Box',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, unique=True, verbose_name='Номер ячейки')),
                ('price', models.FloatField(default=0, verbose_name='Стоимость')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='boxes', to='storage.warehouse', verbose_name='Ячейка')),
            ],
        ),
    ]
