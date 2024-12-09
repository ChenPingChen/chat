from typing import List, Dict
from openai import OpenAI
from .HybridSearchService import HybridSearchService
from django.conf import settings

class ChatResponseService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.hybrid_search = HybridSearchService()
        
    def generate_response(self, query: str, search_results: List[Dict]) -> Dict:
        """生成結構化的回覆"""
        try:
            # 將搜尋結果轉換為提示文本
            context = self._format_search_results(search_results)
            
            # 修改系統提示，限制回答長度
            messages_content = [
                {
                    "role": "system",
                    "content": """你是一個工地安全專家。請提供簡短且重點的回答：
                    1. 回答必須控制在100個tokens以內
                    2. 使用簡潔的語言直接回應用戶問題
                    3. 不需要詳細解釋，只需給出關鍵資訊"""
                },
                {
                    "role": "user",
                    "content": f"問題：{query}\n\n參考資料：{context}"
                }
            ]
            
            # 調整回覆參數
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages_content,
                max_tokens=100,
                temperature=0.2,
                presence_penalty=0.6  # 增加回覆的多樣性
            )
            
            # 構建結構化回覆
            return {
                "answer": response.choices[0].message.content,
                "reference_cases": self._format_reference_cases(search_results)
            }
            
        except Exception as e:
            raise Exception(f"生成回覆時發生錯誤: {str(e)}")
    
    def _format_reference_cases(self, results: List[Dict]) -> List[Dict]:
        """格式化參考案例，突出圖片資訊"""
        formatted_cases = []
        for result in results:
            formatted_cases.append({
                "image_url": result['image_url'],
                "image_path": result['image_path'],
                "violation_info": {
                    "type": result['violation_type'],
                    "time": result['start_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    "details": result['details'],
                    "similarity": f"{result['similarity_score']:.2f}"
                }
            })
        return formatted_cases
            
    def _format_search_results(self, results: List[Dict]) -> str:
        """將搜尋結果格式化為簡潔的提示文本"""
        formatted_text = "相關案例摘要：\n"
        for idx, result in enumerate(results, 1):
            formatted_text += f"案例{idx}: {result['violation_type']} - {result['details'][:50]}...\n"
        return formatted_text
