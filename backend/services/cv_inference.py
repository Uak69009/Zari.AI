"""
ZARI.ai Backend — Computer Vision Inference Service
===================================================
Provides CropDiseaseClassifier interface wrapping EfficientNetV2-B2.
"""

from api.cv_inference import predict as run_predict

class CropDiseaseClassifier:
    """
    Crop disease classifier using PyTorch EfficientNetV2-B2 model.
    """

    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold

    def predict(self, image_bytes: bytes) -> dict:
        """
        Run inference on raw image bytes.
        """
        return run_predict(image_bytes, confidence_threshold=self.confidence_threshold)
