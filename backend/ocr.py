import os

import cv2
import pytesseract


# Use a custom Tesseract path only when one is provided.
# This keeps the code compatible with both Windows and Linux.
tesseract_cmd = os.getenv("TESSERACT_CMD")

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def extract_text(image_path):
    print("    → Reading image...")

    image = cv2.imread(image_path)

    if image is None:
        print("    ✗ Could not read image")
        return ""

    print(
        f"    → Image loaded: "
        f"{image.shape[1]}x{image.shape[0]}"
    )

    max_width = 1800

    if image.shape[1] > max_width:
        scale = max_width / image.shape[1]

        new_width = int(image.shape[1] * scale)
        new_height = int(image.shape[0] * scale)

        image = cv2.resize(
            image,
            (new_width, new_height)
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
        f"Characters extracted: {len(text)}"
    )

    return text