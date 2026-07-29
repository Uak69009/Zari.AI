import torch
import torch.nn as nn
from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights

def build_model(num_classes: int, freeze_backbone: bool = False):
    """
    Builds the EfficientNetV2-S model for ZARI.ai classification.
    
    Args:
        num_classes (int): The number of output classes.
        freeze_backbone (bool): If True, freezes the feature backbone layers.
        
    Returns:
        nn.Module: The configured PyTorch model.
    """
    # Load pretrained EfficientNetV2-S
    weights = EfficientNet_V2_S_Weights.DEFAULT
    model = efficientnet_v2_s(weights=weights)
    
    if freeze_backbone:
        # Freeze all parameters in the feature extractor
        for param in model.features.parameters():
            param.requires_grad = False
            
    # Modify the classifier head
    # EfficientNetV2-S classifier has a dropout layer at index 0 and a linear layer at index 1
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, num_classes)
    
    return model
