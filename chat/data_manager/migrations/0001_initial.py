# Generated by Django 5.1.3 on 2024-12-09 01:44

import django.db.models.deletion
import django.utils.timezone
import pgvector.django.vector
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ViolationEvent',
            fields=[
                ('event_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('violation_type', models.CharField(max_length=50)),
                ('details', models.TextField()),
                ('image_url', models.URLField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('camera_id', models.CharField(max_length=50)),
                ('scene_id', models.CharField(max_length=50)),
                ('image_path', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('processed_status', models.CharField(choices=[('PENDING', '待處理'), ('PROCESSING', '處理中'), ('COMPLETED', '已完成'), ('FAILED', '失敗')], default='PENDING', max_length=20)),
            ],
            options={
                'indexes': [models.Index(fields=['violation_type'], name='data_manage_violati_ac13a7_idx'), models.Index(fields=['start_time'], name='data_manage_start_t_74d88b_idx'), models.Index(fields=['camera_id'], name='data_manage_camera__01eabd_idx'), models.Index(fields=['processed_status'], name='data_manage_process_9e5113_idx')],
            },
        ),
        migrations.CreateModel(
            name='PersonInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person_role', models.CharField(max_length=100)),
                ('person_id', models.CharField(max_length=50)),
                ('equipment', models.JSONField()),
                ('violation_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_manager.violationevent')),
            ],
        ),
        migrations.CreateModel(
            name='VectorStore',
            fields=[
                ('vector_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image_embedding', pgvector.django.vector.VectorField(dimensions=768)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('violation_event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vector_data', to='data_manager.violationevent')),
            ],
            options={
                'indexes': [models.Index(fields=['created_at'], name='data_manage_created_99583b_idx')],
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(blank=True, max_length=100)),
                ('device_state', models.CharField(blank=True, max_length=100)),
                ('violation_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to='data_manager.violationevent')),
            ],
            options={
                'indexes': [models.Index(fields=['device_name'], name='data_manage_device__3e7620_idx'), models.Index(fields=['device_state'], name='data_manage_device__910287_idx')],
            },
        ),
        migrations.CreateModel(
            name='ConstructionVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_name', models.CharField(blank=True, max_length=100)),
                ('vehicle_state', models.CharField(blank=True, max_length=100)),
                ('violation_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='construction_vehicles', to='data_manager.violationevent')),
            ],
            options={
                'indexes': [models.Index(fields=['vehicle_name'], name='data_manage_vehicle_b333bd_idx'), models.Index(fields=['vehicle_state'], name='data_manage_vehicle_641a1a_idx')],
            },
        ),
    ]