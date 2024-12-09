from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from violations_records.data_manager.services.ViolationDataProcessor import ViolationDataProcessor
from violations_records.data_manager.services.VectorStoreService import VectorStoreService
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='post',
    operation_description="處理違規事件資料",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['violation', 'person'],
        properties={
            'violation': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'type': openapi.Schema(type=openapi.TYPE_STRING),
                    'details': openapi.Schema(type=openapi.TYPE_STRING),
                    'imageUrl': openapi.Schema(type=openapi.TYPE_STRING),
                    'time': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'start': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            'end': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        }
                    ),
                }
            ),
            'person': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'person_role': openapi.Schema(type=openapi.TYPE_STRING),
                    'person_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'person_equipment': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                }
            ),
        }
    ),
    responses={
        201: '違規事件資料處理完成',
        400: '處理失敗',
    }
)
@api_view(['POST'])
def process_violation_data(request):
    """
    接收並處理違規事件JSON數據
    
    請求體應為包含違規事件資訊的JSON數據
    """
    try:
        # 1. 驗證接收到的數據
        if not isinstance(request.data, dict):
            return Response(
                {'error': '無效的數據格式'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 處理違規事件資料
        violation_event = ViolationDataProcessor.process_violation_data(request.data)
        
        # 3. 更新狀態為處理中
        violation_event.processed_status = 'PROCESSING'
        violation_event.save()
        
        try:
            # 4. 處理向量化
            vector_service = VectorStoreService()
            vector_store = vector_service.process_and_store_vectors(violation_event)
            
            # 5. 更新處理狀態為完成
            violation_event.processed_status = 'COMPLETED'
            violation_event.save()
            
        except Exception as ve:
            # 向量化處理失敗
            logger.error(f"向量化處理失敗: {str(ve)}")
            violation_event.processed_status = 'FAILED'
            violation_event.save()
            raise
        
        # 6. 準備回應資料
        response_data = {
            'event_id': str(violation_event.event_id),
            'status': 'success',
            'processed_status': violation_event.processed_status,
            'message': '違規事件資料處理完成'
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"處理違規事件資料失敗: {str(e)}")
        return Response(
            {
                'status': 'error',
                'message': '處理失敗',
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def batch_process_violations(request):
    """
    批量處理多筆違規事件JSON數據
    """
    # 確保請求數據是列表格式
    data = request.data
    if not isinstance(data, list):
        return Response(
            {'error': '請求數據必須是陣列格式'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    results = []
    errors = []
    
    for payload in data:
        try:
            with transaction.atomic():
                # 處理單筆資料
                violation_event = ViolationDataProcessor.process_violation_data(payload)
                violation_event.processed_status = 'PROCESSING'
                violation_event.save()
                
                try:
                    # 處理向量化
                    vector_service = VectorStoreService()
                    vector_store = vector_service.process_and_store_vectors(violation_event)
                    violation_event.processed_status = 'COMPLETED'
                    violation_event.save()
                    
                except Exception as ve:
                    violation_event.processed_status = 'FAILED'
                    violation_event.save()
                    raise
                
                results.append({
                    'event_id': str(violation_event.event_id),
                    'status': 'success',
                    'processed_status': violation_event.processed_status
                })
                
        except Exception as e:
            errors.append({
                'payload': payload,
                'error': str(e)
            })
    
    return Response({
        'results': results,
        'errors': errors
    }, status=status.HTTP_207_MULTI_STATUS)