from ocr import extract_text

image_path = r"D:\VeriShield-AI\uploads\test.jpg"

text = extract_text(image_path)

print("\n===== EXTRACTED TEXT =====")
print(text)