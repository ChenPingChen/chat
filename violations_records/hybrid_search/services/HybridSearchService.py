from typing import List, Dict, Optional, Tuple
from django.db.models import Q
from django.db import connection
from violations_records.data_manager.services.TextVectorizeService import TextVectorizeService
import logging
import re
from datetime import datetime, time
from dateutil import parser

class HybridSearchService:
    def __init__(self):
        self.text_vectorizer = TextVectorizeService()
        self.logger = logging.getLogger(__name__)
        
    def _extract_time_info(self, query: str) -> Tuple[Optional[time], Optional[time], str]:
        """
        提取時間範圍信息
        
        Returns:
            Tuple[Optional[time], Optional[time], str]: (開始時間, 結束時間, 清理後的查詢文本)
        """
        start_time = None
        end_time = None
        
        # 處理具體時間點
        time_patterns = [
            (r'(\d{1,2})[:點時](\d{2})?分?', lambda h, m: time(int(h), int(m) if m else 0)),
            (r'([上下]午)(\d{1,2})[:點時](\d{2})?分?', 
             lambda meridiem, h, m: time(int(h) + (12 if meridiem == '下午' and int(h) != 12 else 0), 
                                      int(m) if m else 0))
        ]
        
        # 處理時間範圍描述
        time_range_keywords = {
            '以後': lambda t: (t, time(23, 59, 59)),
            '以前': lambda t: (time(0, 0, 0), t),
            '之後': lambda t: (t, time(23, 59, 59)),
            '之前': lambda t: (time(0, 0, 0), t)
        }
        
        # 先找到所有時間表達式
        for pattern, time_converter in time_patterns:
            matches = list(re.finditer(pattern, query))
            if matches:
                for match in matches:
                    time_str = match.group(0)
                    try:
                        if len(match.groups()) == 2:  # 簡單時間格式
                            extracted_time = time_converter(*match.groups())
                        else:  # 帶上下午的時間格式
                            extracted_time = time_converter(*match.groups())
                        
                        # 檢查時間範圍關鍵詞
                        for keyword, range_converter in time_range_keywords.items():
                            if keyword in query and query.index(keyword) > query.index(time_str):
                                start_time, end_time = range_converter(extracted_time)
                                query = query.replace(time_str + keyword, '').strip()
                                break
                        else:
                            # 如果沒有範圍關鍵詞，設置為具體時間點
                            start_time = extracted_time
                            end_time = extracted_time
                            query = query.replace(time_str, '').strip()
                            
                    except ValueError:
                        continue
                        
        return start_time, end_time, query
    
    def _extract_filters(self, query: str) -> Tuple[Dict, str]:
        """
        從查詢文本中提取過濾條件
        """
        filters = {
            'start_date': None,
            'end_date': None,
            'start_time': None,
            'end_time': None,
            'violation_type': None,
            'exact_match': False,
            'is_violation_query': False
        }
        
        # 提取違規類型
        violation_patterns = [
            r'\b(A[1-9]|B[1-9]|C[1-9])\b',  # 精確的違規代碼
            r'(A[1-9]|B[1-9]|C[1-9])違規',   # 帶有「違規」的查詢
            r'(A[1-9]|B[1-9]|C[1-9])事件'    # 帶有「事件」的查詢
        ]
        
        for pattern in violation_patterns:
            violation_match = re.search(pattern, query)
            if violation_match:
                filters['violation_type'] = violation_match.group(1)
                filters['exact_match'] = True
                filters['is_violation_query'] = True  # 標記為違規類型查詢
                query = query.replace(violation_match.group(0), '').strip()
                break
        
        # 提取日期和日期範圍
        date_patterns = [
            (r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', '%Y-%m-%d'),
            (r'(\d{4}年\d{1,2}月\d{1,2}日)', '%Y年%m月%d日'),
            (r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)', None)
        ]
        
        # 日期範圍關鍵詞
        date_range_keywords = {
            '以後': lambda d: (d, None),
            '之後': lambda d: (d, None),
            '以前': lambda d: (None, d),
            '之前': lambda d: (None, d)
        }
        
        for pattern, date_format in date_patterns:
            match = re.search(pattern, query)
            if match:
                date_str = match.group(1)
                try:
                    if date_format:
                        parsed_date = datetime.strptime(
                            date_str.replace('/', '-'), 
                            date_format
                        )
                    else:
                        parsed_date = parser.parse(date_str)
                    
                    # 檢查日期範圍關鍵詞
                    for keyword, range_converter in date_range_keywords.items():
                        if keyword in query and query.index(keyword) > query.index(date_str):
                            start_date, end_date = range_converter(parsed_date)
                            filters['start_date'] = start_date
                            filters['end_date'] = end_date
                            query = query.replace(date_str + keyword, '').strip()
                            break
                    else:
                        # 如果沒有範圍關鍵詞，設置為具體日期
                        filters['start_date'] = parsed_date
                        filters['end_date'] = parsed_date
                        query = query.replace(date_str, '').strip()
                    break
                except ValueError:
                    continue
        
        # 2. 提取時間範圍
        start_time, end_time, query = self._extract_time_info(query)
        filters['start_time'] = start_time
        filters['end_time'] = end_time
        
        return filters, query.strip()
    
    def _build_sql_with_filters(self, filters: Dict, clean_query: str, query_vector: List[float], top_k: int) -> Tuple[str, List]:
        """
        根據過濾條件構建SQL查詢
        """
        sql = """
            WITH filtered_events AS (
                SELECT ve.* 
                FROM data_manager_violationevent ve 
                WHERE 1=1
        """
        params = []
        
        # 違規類型查詢的處理
        if filters['violation_type'] and filters['is_violation_query']:
            sql += """
                AND ve.violation_type = %s
            """
            params.append(filters['violation_type'])
        
        # 日期範圍過濾
        if filters.get('start_date'):
            sql += """
                AND DATE(ve.start_time) >= %s
            """
            params.append(filters['start_date'].date())
        
        if filters.get('end_date'):
            sql += """
                AND DATE(ve.start_time) <= %s
            """
            params.append(filters['end_date'].date())
        
        # 時間範圍過濾
        if filters.get('start_time'):
            sql += """
                AND EXTRACT(HOUR FROM ve.start_time) * 60 + 
                    EXTRACT(MINUTE FROM ve.start_time) >= %s
            """
            start_minutes = filters['start_time'].hour * 60 + filters['start_time'].minute
            params.append(start_minutes)
        
        if filters.get('end_time'):
            sql += """
                AND EXTRACT(HOUR FROM ve.start_time) * 60 + 
                    EXTRACT(MINUTE FROM ve.start_time) <= %s
            """
            end_minutes = filters['end_time'].hour * 60 + filters['end_time'].minute
            params.append(end_minutes)
        
        sql += """
            ),
            keyword_search AS (
                SELECT 
                    fe.event_id,
                    CASE 
        """
        
        # 評分邏輯
        if filters['is_violation_query']:
            sql += """
                        WHEN fe.violation_type = %s THEN 1.0
                        WHEN fe.violation_type LIKE %s THEN 0.0
                        ELSE 0.0
            """
            params.extend([
                filters['violation_type'],
                f"%{filters['violation_type']}%"
            ])
        else:
            sql += """
                        WHEN fe.details ILIKE %s THEN 0.8
                        WHEN fe.violation_type ILIKE %s THEN 0.4
                        ELSE 0.0
            """
            params.extend([
                f"%{clean_query}%",
                f"%{clean_query}%"
            ])
        
        sql += """
                        END as text_score
                    FROM filtered_events fe
                ),
                vector_search AS (
                    SELECT 
                        vs.violation_event_id,
                        1.0 / (1.0 + (vs.image_embedding <-> %s::vector)) as vector_score
                    FROM data_manager_vectorstore vs
                    JOIN filtered_events fe ON vs.violation_event_id = fe.event_id
                )
                SELECT 
                    ve.event_id,
                    ve.violation_type,
                    ve.details,
                    ve.image_url,
                    ve.image_path,
                    ve.start_time,
                    CASE 
                        WHEN %s AND ve.violation_type = %s THEN 1.0
                        ELSE COALESCE(ks.text_score, 0.0) * 0.8 +
                             COALESCE(vs.vector_score, 0.0) * 0.2
                    END as similarity_score
                FROM filtered_events ve
                LEFT JOIN keyword_search ks ON ve.event_id = ks.event_id
                LEFT JOIN vector_search vs ON ve.event_id = vs.violation_event_id
                ORDER BY similarity_score DESC
                LIMIT %s
        """
        
        # 添加最後的參數
        params.extend([
            query_vector,
            filters['exact_match'],
            filters.get('violation_type', ''),
            top_k
        ])
        
        return sql, params
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        執行混合搜索
        
        Args:
            query: 搜索查詢文本
            top_k: 返回結果數量
            
        Returns:
            List[Dict]: 搜索結果列表
        """
        try:
            # 1. 提取過濾條件
            filters, clean_query = self._extract_filters(query)
            
            # 2. 向量化清理後的查詢文本
            query_vector = self.text_vectorizer.vectorize(clean_query)
            
            # 3. 構建SQL查詢
            sql, params = self._build_sql_with_filters(filters, clean_query, query_vector, top_k)
            
            # 4. 執行查詢
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'event_id': str(row[0]),
                        'violation_type': row[1],
                        'details': row[2],
                        'image_url': row[3],
                        'image_path': row[4],
                        'start_time': row[5],
                        'similarity_score': float(row[6])
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"混合搜索失敗: {str(e)}")
            raise Exception(f"混合搜索失敗: {str(e)}")
