import logging
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoImageProcessor
from PIL import Image
import numpy as np
from django.conf import settings


class ImageVectorizeService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.processor = AutoImageProcessor.from_pretrained(settings.VISION_VECTOR_MODEL_PATH)
        self.model = AutoModel.from_pretrained(
            settings.VISION_VECTOR_MODEL_PATH, 
            trust_remote_code=True
        )
        
    def vectorize(self, image_path: str) -> np.ndarray:
        """
        將單一圖片轉換為向量
        
        Args:
            image_path (str): 圖片檔案路徑
            
        Returns:
            np.ndarray: 圖片的向量表示
            
        Raises:
            Exception: 當向量化過程發生錯誤時
        """
        try:
            # 讀取並處理圖片
            image = Image.open(image_path)
            inputs = self.processor(image, return_tensors="pt")
            
            # 生成向量
            with torch.no_grad():
                img_emb = self.model(**inputs).last_hidden_state
                img_embeddings = F.normalize(img_emb[:, 0], p=2, dim=1)
                
            return img_embeddings.numpy()[0]  # 轉換為 numpy array 並取出第一個結果
            
        except Exception as e:
            self.logger.error(f"圖片向量化失敗: {str(e)}")
            raise Exception(f"圖片向量化失敗: {str(e)}")