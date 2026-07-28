"""
ZARI.ai ML Pipeline — ONNX Export Script
Exports a trained EfficientNetV2-S PyTorch model to ONNX format
for lightweight CPU inference in the backend.
"""

import argparse
import os
import sys
import torch
import torch.onnx


def export_to_onnx(
    checkpoint_path: str,
    output_path: str,
    num_classes: int,
    input_size: int = 384,
    opset_version: int = 17,
):
    """
    Export a trained EfficientNetV2-S model to ONNX format.

    Args:
        checkpoint_path: Path to the PyTorch .pth checkpoint.
        output_path: Path for the output .onnx file.
        num_classes: Number of disease classes.
        input_size: Model input resolution (default 384 for EfficientNetV2-S).
        opset_version: ONNX opset version.
    """
    import timm

    print(f"Loading model from: {checkpoint_path}")

    # Create model architecture
    model = timm.create_model(
        "tf_efficientnetv2_s",
        pretrained=False,
        num_classes=num_classes,
    )

    # Load trained weights
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    if "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

    model.eval()

    # Create dummy input
    dummy_input = torch.randn(1, 3, input_size, input_size)

    # Export to ONNX
    print(f"Exporting to ONNX: {output_path}")
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},
            "output": {0: "batch_size"},
        },
    )

    # Verify exported model
    import onnx

    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ ONNX export successful!")
    print(f"   Output: {output_path}")
    print(f"   Size: {file_size_mb:.1f} MB")
    print(f"   Classes: {num_classes}")
    print(f"   Input shape: (1, 3, {input_size}, {input_size})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export ZARI.ai model to ONNX")
    parser.add_argument(
        "--checkpoint", type=str, required=True,
        help="Path to PyTorch .pth checkpoint",
    )
    parser.add_argument(
        "--output", type=str, default="../../backend/models/efficientnetv2s_zari.onnx",
        help="Output ONNX file path",
    )
    parser.add_argument(
        "--num-classes", type=int, required=True,
        help="Number of disease classes",
    )
    parser.add_argument(
        "--input-size", type=int, default=384,
        help="Model input resolution (default: 384)",
    )

    args = parser.parse_args()

    export_to_onnx(
        checkpoint_path=args.checkpoint,
        output_path=args.output,
        num_classes=args.num_classes,
        input_size=args.input_size,
    )
