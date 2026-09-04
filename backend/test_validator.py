from ocr import extract_text

image_path = r"D:\VeriShield-AI\uploads\test.jpg"

print("===== OCR TEST =====")

text = extract_text(image_path)

print("\n===== ACTUAL OCR OUTPUT =====")
print(repr(text))

print("\n===== END =====")