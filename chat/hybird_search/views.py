from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .services.HybridSearchService import HybridSearchService
from .services.ChatResponseService import ChatResponseService
import logging

class HybridSearchView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_service = HybridSearchService()
        self.chat_response_service = ChatResponseService()
        self.logger = logging.getLogger(__name__)

    @swagger_auto_schema(
        operation_description="執行混合搜索查詢（輸入查詢文字即可）",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['query'],
            properties={
                'query': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='搜索查詢文字，例如："未戴安全帽"'
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="成功執行搜索",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'event_id': openapi.Schema(type=openapi.TYPE_STRING),
                                    'violation_type': openapi.Schema(type=openapi.TYPE_STRING),
                                    'details': openapi.Schema(type=openapi.TYPE_STRING),
                                    'image_url': openapi.Schema(type=openapi.TYPE_STRING),
                                    'start_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                                    'similarity_score': openapi.Schema(type=openapi.TYPE_NUMBER),
                                }
                            )
                        ),
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            ),
            400: '查詢文字不能為空',
            500: '搜索請求處理失敗'
        }
    )
    def post(self, request):
        try:
            query = request.data.get('query')
            
            if not query:
                return Response(
                    {'error': '查詢文字不能為空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            search_results = self.search_service.search(query=query)
            results = self.chat_response_service.generate_response(query, search_results)
            
            return Response({
                'results': results,
            })
            
        except Exception as e:
            self.logger.error(f"搜索請求處理失敗: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
