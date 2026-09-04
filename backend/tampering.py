from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import os
import tempfile


def detect_tampering(image_path):
    """
    Basic image-forensics based tampering analysis.

    This uses JPEG Error Level Analysis (ELA) to look for
    unusual compression differences across the image.

    IMPORTANT:
    This is an anomaly detector, not a definitive forgery detector.
    """

    try:
        # -----------------------------------------------------
        # Load original image
        # -----------------------------------------------------

        original = Image.open(image_path).convert("RGB")

        # -----------------------------------------------------
        # Create temporary JPEG recompression
        # -----------------------------------------------------

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".jpg",
                delete=False
            ) as temp_file:

                temp_path = temp_file.name

            original.save(
                temp_path,
                "JPEG",
                quality=90
            )

            recompressed = Image.open(
                temp_path
            ).convert("RGB")

        finally:

            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        # -----------------------------------------------------
        # Calculate ELA difference
        # -----------------------------------------------------

        difference = ImageChops.difference(
            original,
            recompressed
        )

        diff_array = np.asarray(
            difference
        ).astype(np.float32)

        # Average pixel difference
        mean_difference = float(
            np.mean(diff_array)
        )

        # Maximum difference
        max_difference = float(
            np.max(diff_array)
        )

        # -----------------------------------------------------
        # Normalize score
        # -----------------------------------------------------

        # ELA values are normally relatively small.
        # This converts the raw difference into a
        # more understandable 0-100 anomaly score.

        anomaly_score = min(
            100.0,
            mean_difference * 4.0
        )

        # -----------------------------------------------------
        # Classification
        # -----------------------------------------------------

        if anomaly_score >= 60:
            result = "HIGH RISK"

        elif anomaly_score >= 30:
            result = "SUSPICIOUS"

        else:
            result = "LOW RISK"

        # -----------------------------------------------------
        # Return result
        # -----------------------------------------------------

        return {
            "tampering_result": result,
            "difference_score": round(
                anomaly_score,
                2
            ),
            "raw_ela_score": round(
                mean_difference,
                4
            ),
            "max_difference": round(
                max_difference,
                2
            )
        }

    except Exception as e:

        return {
            "tampering_result": "UNKNOWN",
            "difference_score": 0,
            "message": f"Tampering analysis failed: {str(e)}"
        }