from tampering import detect_tampering


image_path = r"D:\VeriShield-AI\uploads\test.jpg"

result = detect_tampering(image_path)

print("\n===== TAMPERING ANALYSIS =====")

print("Result:", result["tampering_result"])
print("Difference Score:", result["difference_score"])