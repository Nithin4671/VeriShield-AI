import os
import shutil

import cv2
import pytesseract


# =====================================================
# TESSERACT CONFIGURATION
# =====================================================

# 1. Prefer the environment variable if provided.
tesseract_cmd = os.getenv("TESSERACT_CMD")

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

else:
    # 2. Try to find Tesseract automatically from PATH.
    tesseract_from_path = shutil.which("tesseract")

    if tesseract_from_path:
        pytesseract.pytesseract.tesseract_cmd = (
            tesseract_from_path
        )

    # 3. Windows fallback.
    #    This path is used only if the file actually exists.
    elif os.name == "nt":

        windows_tesseract = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        if os.path.exists(windows_tesseract):
            pytesseract.pytesseract.tesseract_cmd = (
                windows_tesseract
            )


# =====================================================
# OCR
# =====================================================

def extract_text(image_path):

    print("    → Reading image...")

    image = cv2.imread(image_path)

    if image is None:

        print(
            "    ✗ Could not read image"
        )

        return ""

    print(
        f"    → Image loaded: "
        f"{image.shape[1]}x{image.shape[0]}"
    )

    max_width = 1800

    if image.shape[1] > max_width:

        scale = (
            max_width /
            image.shape[1]
        )

        new_width = int(
            image.shape[1] * scale
        )

        new_height = int(
            image.shape[0] * scale
        )

        image = cv2.resize(
            image,
            (
                new_width,
                new_height
            )
        )

        print(
            f"    → Resized to "
            f"{new_width}x{new_height}"
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    print("    → Running OCR...")

    try:

        text = pytesseract.image_to_string(
            gray,
            config="--psm 11"
        )

        if len(text.strip()) < 20:

            print(
                "    → OCR text too short, "
                "trying enhanced image..."
            )

            enhanced = cv2.convertScaleAbs(
                gray,
                alpha=1.3,
                beta=10
            )

            text = pytesseract.image_to_string(
                enhanced,
                config="--psm 11"
            )

        print(
            f"    → OCR finished. "
            f"Characters extracted: "
            f"{len(text)}"
        )

        return text

    except Exception as e:

        print(
            f"    ✗ OCR ERROR: {str(e)}"
        )

        return ""