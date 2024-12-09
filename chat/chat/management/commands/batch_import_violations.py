from django.core.management.base import BaseCommand
import json
import os
from data_manager.views import batch_process_violations
from rest_framework.test import APIRequestFactory

class Command(BaseCommand):
    help = '批量導入違規事件數據和相關圖片'

    def add_arguments(self, parser):
        parser.add_argument('data_dir', type=str, help='包含 JSON 文件和圖片的目錄路徑')

    def handle(self, *args, **options):
        data_dir = options['data_dir']
        violations_data = []

        # 遍歷目錄中的所有 JSON 文件
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(data_dir, filename)
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        violation_data = json.load(f)
                        
                        # 更新圖片路徑
                        image_filename = os.path.basename(violation_data['image_path'])
                        violation_data['image_path'] = os.path.join(data_dir, image_filename)
                        
                        # 確認圖片文件存在
                        if os.path.exists(violation_data['image_path']):
                            violations_data.append(violation_data)
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'警告：找不到圖片文件 {violation_data["image_path"]}'
                                )
                            )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'處理 {filename} 時發生錯誤：{str(e)}')
                    )

        if violations_data:
            # 使用 APIRequestFactory 創建請求
            factory = APIRequestFactory()
            request = factory.post(
                '/data-manager/batch/',
                data=violations_data,
                format='json'
            )

            # 輸出調試信息
            self.stdout.write(self.style.SUCCESS(f'準備處理 {len(violations_data)} 筆數據'))
            
            try:
                # 調用批量處理函數
                response = batch_process_violations(request)
                
                # 輸出處理結果
                if hasattr(response, 'data'):
                    response_data = response.data
                    
                    if isinstance(response_data, dict):
                        if 'results' in response_data:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'成功處理 {len(response_data["results"])} 筆數據'
                                )
                            )
                            # 輸出成功處理的數據詳情
                            for result in response_data['results']:
                                self.stdout.write(f'  - 事件 ID: {result.get("event_id")}')
                        
                        if 'errors' in response_data:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'處理失敗 {len(response_data["errors"])} 筆'
                                )
                            )
                            for error in response_data['errors']:
                                self.stdout.write(f'  - 錯誤: {error}')
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'未預期的回應格式: {response_data}')
                        )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'處理過程中發生錯誤: {str(e)}')
                )
                
        else:
            self.stdout.write(self.style.WARNING('沒有找到有效的違規事件數據'))