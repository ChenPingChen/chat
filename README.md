需要先行安裝與設備相匹配的torch與cuda版本

## 安裝步驟

1. 進入專案目錄
```bash
cd chat
```

2. 安裝套件
```bash
pip install -r requirement.txt  
```

3. 建立 PostgreSQL 資料庫
```bash
python manage.py create_postgresql
```

4. 批量上傳違規事件
```bash
python manage.py batch_import_violations /path/to/your/folder
```
