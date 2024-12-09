import logging
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np
from django.conf import settings


class TextVectorizeService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tokenizer = AutoTokenizer.from_pretrained(settings.TEXT_VECTOR_MODEL_PATH)
        self.model = AutoModel.from_pretrained(
            settings.TEXT_VECTOR_MODEL_PATH,
            trust_remote_code=True
        )
        self.model.eval()
        
    def _mean_pooling(self, model_output, attention_mask):
        """
        mean_pooling，用於生成文本向量
        """
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
    def vectorize(self, text: str) -> np.ndarray:
        """
        將文本轉換為向量
        
        Args:
            text (str): 輸入文本
            
        Returns:
            np.ndarray: 文本的向量表示
            
        Raises:
            Exception: 當向量化過程發生錯誤時
        """
        try:
            text = text.strip()
            
            # 對文本進行編碼
            encoded_input = self.tokenizer(
                [text], 
                padding=True, 
                truncation=True, 
                return_tensors='pt'
            )
            
            # 生成向量
            with torch.no_grad():
                model_output = self.model(**encoded_input)
                
            # 處理向量
            text_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
            text_embeddings = F.layer_norm(text_embeddings, normalized_shape=(text_embeddings.shape[1],))
            text_embeddings = F.normalize(text_embeddings, p=2, dim=1)
            
            return text_embeddings.numpy()[0].tolist()  # 轉換為 numpy array 並取出第一個結果
            
        except Exception as e:
            self.logger.error(f"文字向量化失敗: {str(e)}")
            raise Exception(f"文字向量化失敗: {str(e)}")
