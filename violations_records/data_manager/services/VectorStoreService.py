from violations_records.data_manager.models import ViolationEvent, VectorStore
from violations_records.data_manager.services.TextVectorizeService import TextVectorizeService
from violations_records.data_manager.services.ImageVectorizeService import ImageVectorizeService
import logging


class VectorStoreService:
    def __init__(self):
        self.text_vectorizer = TextVectorizeService()
        self.image_vectorizer = ImageVectorizeService()
        self.logger = logging.getLogger(__name__)
    
    
    def process_and_store_vectors(self, violation_event: ViolationEvent) -> VectorStore:
        """
        處理並儲存所有向量資料
        
        Args:
            violation_event: 違規事件實例
            
        Returns:
            VectorStore: 向量儲存實例
        """
        try:
            # 1. 處理圖片向量
            image_embedding = self.image_vectorizer.vectorize(violation_event.image_path)
            
            # 2. 儲存所有向量資料
            vector_store = VectorStore.objects.create(
                violation_event=violation_event,
                image_embedding=image_embedding,
            )
            
            self.logger.info(f"成功處理並儲存向量資料: {vector_store.vector_id}")
            return vector_store
            
        except Exception as e:
            self.logger.error(f"向量處理與儲存失敗: {str(e)}")
            raise