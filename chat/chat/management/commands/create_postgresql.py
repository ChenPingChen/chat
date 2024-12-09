# management/commands/create_postgresql.py
from django.core.management.base import BaseCommand
from django.conf import settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess

class Command(BaseCommand):
    help = 'Creates a PostgreSQL database and runs migrations'

    def handle(self, *args, **options):
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']
        db_password = settings.DATABASES['default']['PASSWORD']
        superuser = settings.DATABASES['superuser']['USER']
        superuser_password = settings.DATABASES['superuser']['PASSWORD']
        
        # 創建用戶並授予權限
        self.create_user(db_user, db_password, superuser, superuser_password)
        
        # 創建資料庫
        self.create_database(db_name, db_user, db_password)
        
        # 運行資料庫遷移
        self.run_migrations()

    def create_user(self, db_user, db_password, superuser, superuser_password):
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=superuser,
                password=superuser_password,
                host=settings.DATABASES['superuser']['HOST']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            cur.execute(f"ALTER USER {db_user} CREATEDB")
            
            self.stdout.write(self.style.SUCCESS(f"User '{db_user}' created successfully"))

        except psycopg2.Error as e:
            self.stdout.write(self.style.ERROR(f"Error creating user: {e}"))

    def create_database(self, db_name, db_user, db_password):
        try:
            conn = psycopg2.connect(
                dbname='postgres',
                user=db_user,
                password=db_password,
                host=settings.DATABASES['default']['HOST']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            cur.execute(f"CREATE DATABASE {db_name}")
            
            # 關閉現有連接
            cur.close()
            conn.close()
            
            # 連接到新創建的數據庫
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=settings.DATABASES['default']['HOST']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            # 創建 vector 擴展
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            self.stdout.write(self.style.SUCCESS(f"Database '{db_name}' created successfully with vector extension"))

        except psycopg2.Error as e:
            self.stdout.write(self.style.ERROR(f"Error creating database: {e}"))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def run_migrations(self):
        subprocess.run(['python', 'manage.py', 'makemigrations'])
        subprocess.run(['python', 'manage.py', 'migrate'])

        self.stdout.write(self.style.SUCCESS("Migrations applied successfully"))