from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import shutil


from backend.ocr import extract_text
from backend.validator import extract_fields, validate_fields
from backend.tampering import detect_tampering
from backend.face_verification import detect_face
from backend.face_matching import match_faces


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="VeriShield AI",
    description="AI-Based Fake Identity & Document Screening System",
    version="1.0.0"
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# FRONTEND
# ============================================================

@app.get("/app")
def frontend():
    return FileResponse("frontend/index.html")


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "VeriShield AI is running!",
        "project": "AI-Based Fake Identity & Document Screening System",
        "status": "Online"
    }


# ============================================================
# SIMPLE UPLOAD ENDPOINT
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    allowed_types = {
        "image/jpeg",
        "image/png"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG files are allowed."
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "file_type": file.content_type,
        "status": "Ready for analysis"
    }


# ============================================================
# IDENTITY ANALYSIS
# ============================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    selfie: UploadFile = File(...)
):

    print("\n")
    print("=" * 60)
    print("             VERISHIELD AI ANALYSIS")
    print("=" * 60)


    # ========================================================
    # FILE VALIDATION
    # ========================================================

    allowed_types = {
        "image/jpeg",
        "image/png"
    }

    if file.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Identity document must be a JPG or PNG image."
        )

    if selfie.content_type not in allowed_types:

        raise HTTPException(
            status_code=400,
            detail="Selfie must be a JPG or PNG image."
        )


    # ========================================================
    # SAVE IDENTITY DOCUMENT
    # ========================================================

    print("\n[0] Saving identity document...")

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    print("[0] Identity document saved.")


    # ========================================================
    # SAVE SELFIE
    # ========================================================

    print("[0] Saving selfie...")

    selfie_path = UPLOAD_DIR / selfie.filename

    with selfie_path.open("wb") as buffer:
        shutil.copyfileobj(
            selfie.file,
            buffer
        )

    print("[0] Selfie saved.")


    # ========================================================
    # OCR
    # ========================================================

    print("\n[1] Starting OCR...")

    try:

        extracted_text = extract_text(
            str(file_path)
        )

    except Exception as e:

        print(
            "[1] OCR ERROR:",
            str(e)
        )

        extracted_text = ""

    print(
        "[1] OCR COMPLETE"
    )

    print(
        f"[1] Extracted characters: "
        f"{len(extracted_text)}"
    )


    # ========================================================
    # DOCUMENT FIELD EXTRACTION
    # ========================================================

    print("\n[2] Extracting document fields...")

    try:

        fields = extract_fields(
            extracted_text
        )

    except Exception as e:

        print(
            "[2] FIELD EXTRACTION ERROR:",
            str(e)
        )

        fields = {
            "document_type": "UNKNOWN",
            "document_number": None,
            "name": None,
            "date_of_birth": None,
            "gender": None,
            "nationality": None,
            "date_of_issue": None,
            "date_of_expiry": None
        }

    print(
        "[2] Fields:",
        fields
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    print("\n[3] Validating document...")

    try:

        validation_issues = validate_fields(
            fields
        )

    except Exception as e:

        print(
            "[3] VALIDATION ERROR:",
            str(e)
        )

        validation_issues = [
            "Unable to validate document"
        ]

    print(
        "[3] Validation:",
        validation_issues
    )


    # ========================================================
    # TAMPERING DETECTION
    # ========================================================

    print("\n[4] Starting tampering detection...")

    try:

        tampering = detect_tampering(
            str(file_path)
        )

    except Exception as e:

        print(
            "[4] TAMPERING ERROR:",
            str(e)
        )

        tampering = {
            "tampering_result": "UNKNOWN",
            "difference_score": 0,
            "message": "Unable to perform tampering analysis"
        }

    print(
        "[4] Tampering:",
        tampering
    )


    # ========================================================
    # FACE DETECTION - ID DOCUMENT
    # ========================================================

    print("\n[5] Detecting face on identity document...")

    try:

        face_result = detect_face(
            str(file_path)
        )

    except Exception as e:

        print(
            "[5] ID FACE DETECTION ERROR:",
            str(e)
        )

        face_result = {
            "face_detected": False,
            "face_count": 0,
            "message": "Unable to detect face"
        }

    print(
        "[5] ID face result:",
        face_result
    )


    # ========================================================
    # FACE DETECTION - SELFIE
    # ========================================================

    print("\n[6] Detecting face in current selfie...")

    try:

        selfie_face_result = detect_face(
            str(selfie_path)
        )

    except Exception as e:

        print(
            "[6] SELFIE FACE DETECTION ERROR:",
            str(e)
        )

        selfie_face_result = {
            "face_detected": False,
            "face_count": 0,
            "message": "Unable to detect face"
        }

    print(
        "[6] Selfie face result:",
        selfie_face_result
    )


    # ========================================================
    # FACE MATCHING
    # ========================================================

    print("\n[7] Starting face matching...")

    try:

        if (
            face_result.get("face_detected", False)
            and
            selfie_face_result.get("face_detected", False)
        ):

            face_match_result = match_faces(
                str(file_path),
                str(selfie_path)
            )

        else:

            print(
                "[7] Face matching skipped."
            )

            face_match_result = {
                "match": False,
                "similarity_score": 0,
                "threshold": 0.363,
                "message": (
                    "Face matching not performed "
                    "because a valid face was not "
                    "detected in both images."
                ),
                "id_faces_detected": face_result.get(
                    "face_count",
                    0
                ),
                "selfie_faces_detected": selfie_face_result.get(
                    "face_count",
                    0
                )
            }

    except Exception as e:

        print(
            "[7] FACE MATCHING ERROR:",
            str(e)
        )

        face_match_result = {
            "match": False,
            "similarity_score": 0,
            "threshold": 0.363,
            "message": (
                "Unable to perform face matching"
            ),
            "id_faces_detected": face_result.get(
                "face_count",
                0
            ),
            "selfie_faces_detected": selfie_face_result.get(
                "face_count",
                0
            )
        }

    print(
        "[7] Face matching complete:"
    )

    print(
        face_match_result
    )


    # ========================================================
    # RISK SCORING
    # ========================================================

    print("\n[8] Calculating risk score...")

    risk_score = 0

    risk_factors = []


    # --------------------------------------------------------
    # DOCUMENT TYPE
    # --------------------------------------------------------

    if fields.get("document_type") == "UNKNOWN":

        risk_score += 10

        risk_factors.append(
            "Unable to identify document type"
        )


    # --------------------------------------------------------
    # VALIDATION ISSUES
    # --------------------------------------------------------

    for issue in validation_issues:

        risk_score += 20

        risk_factors.append(
            issue
        )


    # --------------------------------------------------------
    # TAMPERING
    # --------------------------------------------------------

    tampering_result = str(
        tampering.get(
            "tampering_result",
            "UNKNOWN"
        )
    ).upper()


    if tampering_result == "SUSPICIOUS":

        risk_score += 30

        risk_factors.append(
            "Suspicious signs of document tampering"
        )


    elif tampering_result == "HIGH RISK":

        risk_score += 60

        risk_factors.append(
            "High-risk document tampering detected"
        )


    # --------------------------------------------------------
    # ID FACE MISSING
    # --------------------------------------------------------

    if not face_result.get(
        "face_detected",
        False
    ):

        risk_score += 20

        risk_factors.append(
            "No face detected on identity document"
        )


    # --------------------------------------------------------
    # SELFIE FACE MISSING
    # --------------------------------------------------------

    if not selfie_face_result.get(
        "face_detected",
        False
    ):

        risk_score += 20

        risk_factors.append(
            "No human face detected in current selfie"
        )


    # --------------------------------------------------------
    # FACE MISMATCH
    # --------------------------------------------------------

    if (
        face_match_result.get(
            "id_faces_detected",
            0
        ) > 0

        and

        face_match_result.get(
            "selfie_faces_detected",
            0
        ) > 0
    ):

        if not face_match_result.get(
            "match",
            False
        ):

            risk_score += 40

            risk_factors.append(
                "Identity document face does not "
                "match current selfie"
            )


    # ========================================================
    # LIMIT SCORE
    # ========================================================

    risk_score = min(
        risk_score,
        100
    )


    # ========================================================
    # FINAL STATUS
    # ========================================================

    if risk_score >= 60:

        final_status = "HIGH RISK"

    elif risk_score >= 20:

        final_status = "SUSPICIOUS"

    else:

        final_status = "VERIFIED"


    # ========================================================
    # CLEAN RISK FACTORS
    # ========================================================

    # Remove duplicates while preserving order

    risk_factors = list(
        dict.fromkeys(
            risk_factors
        )
    )


    print(
        f"\n[8] Risk Score: "
        f"{risk_score}/100"
    )

    print(
        f"[8] Final Status: "
        f"{final_status}"
    )

    print(
        "[8] Risk Factors:",
        risk_factors
    )


    # ========================================================
    # FINAL RESPONSE
    # ========================================================

    print("\n")
    print("=" * 60)
    print("             ANALYSIS COMPLETE")
    print("=" * 60)
    print("\n")


    return {

        "status": final_status,

        "risk_score": risk_score,

        "risk_factors": risk_factors,

        "document_fields": fields,

        "validation_issues": validation_issues,

        "tampering": tampering,

        "face_verification": face_result,

        "selfie_face_verification": selfie_face_result,

        "face_matching": face_match_result,

        "extracted_text": extracted_text
    }