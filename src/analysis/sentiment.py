"""뉴스 감성 분석기 (BERT)"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict
from ..logger import get_logger

logger = get_logger(__name__)

class SentimentAnalyzer:
    """
    BERT 기반 금융 뉴스 감성 분석기
    Model: snunlp/KR-FinBert-SC
    """
    
    MODEL_NAME = "snunlp/KR-FinBert-SC"
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading Sentiment Model ({self.MODEL_NAME}) on {self.device}...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            
    def analyze(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        텍스트 리스트의 감성 분석
        
        Returns:
            List[Dict]: [{'positive': 0.9, 'negative': 0.1, 'neutral': 0.0}, ...]
        """
        if not self.model or not texts:
            return [{'positive': 0.0, 'negative': 0.0, 'neutral': 0.0, 'score': 0.0}] * len(texts)
            
        results = []
        
        try:
            inputs = self.tokenizer(
                texts, 
                return_tensors='pt', 
                padding=True, 
                truncation=True, 
                max_length=128
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # KR-FinBert-SC labels: 0: negative, 1: neutral, 2: positive
            for prob in probs:
                results.append({
                    'negative': float(prob[0]),
                    'neutral': float(prob[1]),
                    'positive': float(prob[2]),
                    'score': float(prob[2] - prob[0])  # 종합 점수 (-1 ~ 1)
                })
                
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            
        return results

if __name__ == "__main__":
    # 테스트 코드
    from ..logger import setup_logging
    setup_logging()
    
    analyzer = SentimentAnalyzer()
    texts = [
        "삼성전자, 역대 최고 실적 달성 전망",
        "금리 인상 우려에 증시 하락세 지속",
        "현대차, 신형 전기차 출시 예정"
    ]
    scores = analyzer.analyze(texts)
    for text, score in zip(texts, scores):
        print(f"Text: {text}")
        print(f"Score: {score['score']:.2f} (Pos: {score['positive']:.2f}, Neg: {score['negative']:.2f})")
        print("-" * 30)
