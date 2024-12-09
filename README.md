需要先行安裝與設備相匹配的torch與cuda版本


1. 將violations_records複製到django專案目錄下

2. 修改settings.py設定
```python
INSTALLED_APPS = [
    ...
    'violations_records.data_manager',
    'violations_records.hybrid_search',
    ...
]
```

3. 於settings.py加入相關環境變數
```python
# OPENAI
OPENAI_API_KEY="your_api_key"
OPENAI_MODEL="gpt-4o-mini"

#向量模型
VISION_VECTOR_MODEL_PATH="nomic-ai/nomic-embed-vision-v1.5"
TEXT_VECTOR_MODEL_PATH="nomic-ai/nomic-embed-text-v1.5"
```

4. 於settings.py加入資料庫配置
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'chat_database',   # 想要創建的數據庫名稱
        'USER': 'postgres',        # 想要創建的用戶名
        'PASSWORD': 'mycena',      # 用戶的密碼
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'superuser': {
        'USER': 'postgres',  
        'PASSWORD': 'mycena', 
        'HOST': 'localhost', 
    }
}
```

5. 將violations_records/management複製到django專案目錄下
```bash
mv violations_records/management {your_django_project_name}/
```

6. 運行django專案
```bash
python manage.py runserver
```

7. 建立資料庫
```bash
python manage.py create_postgresql
```

8. 批量上傳違規事件
```bash
python manage.py batch_import_violations /path/to/your/folder
```