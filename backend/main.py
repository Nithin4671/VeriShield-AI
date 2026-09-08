import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.ocr import extract_text
from backend.validator import extract_fields, validate_fields
from backend.tampering import detect_tampering
from backend.face_verification import detect_face
from backend.face_matching import match_faces

from backend.otp import (
    send_otp,
    verify_otp,
    is_phone_verified
)


# =====================================================
# APP CONFIGURATION
# =====================================================

app = FastAPI(
    title="VeriShield AI",
    description="AI-Based Fake Identity & Document Screening System",
    version="1.0"
)


# =====================================================
# DIRECTORIES
# =====================================================

BASE_DIR = Path(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

UPLOAD_DIR = BASE_DIR / "uploads"
FRONTEND_DIR = BASE_DIR / "frontend"

UPLOAD_DIR.mkdir(
    exist_ok=True
)


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():

    return {
        "message": "VeriShield AI is running!",
        "project": "AI-Based Fake Identity & Document Screening System",
        "status": "Online"
    }


# =====================================================
# FRONTEND
# =====================================================

@app.get("/app")
async def serve_frontend():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# =====================================================
# OTP MODELS
# =====================================================

class OTPRequest(BaseModel):
    mobile: str


class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str


# =====================================================
# SEND DEMO OTP
# =====================================================

@app.post("/send-otp")
async def send_otp_endpoint(
    request: OTPRequest
):

    mobile = request.mobile.strip()

    # Validate Indian 10-digit mobile number
    if not mobile.isdigit() or len(mobile) != 10:

        return {
            "success": False,
            "message": (
                "Please enter a valid "
                "10-digit mobile number."
            )
        }

    print()
    print(
        "============================================================"
    )
    print("                 VERISHIELD DEMO OTP")
    print(
        "============================================================"
    )
    print(
        f"Mobile Number : {mobile}"
    )

    result = send_otp(mobile)

    print(
        "============================================================"
    )
    print()

    return result


# =====================================================
# VERIFY DEMO OTP
# =====================================================

@app.post("/verify-otp")
async def verify_otp_endpoint(
    request: OTPVerifyRequest
):

    mobile = request.mobile.strip()
    otp = request.otp.strip()

    # Validate mobile
    if not mobile.isdigit() or len(mobile) != 10:

        return {
            "success": False,
            "message": (
                "Please enter a valid "
                "10-digit mobile number."
            )
        }

    # Validate OTP
    if not otp.isdigit() or len(otp) != 6:

        return {
            "success": False,
            "message": (
                "Please enter a valid "
                "6-digit OTP."
            )
        }

    result = verify_otp(
        mobile,
        otp
    )

    if result.get("success"):

        print(
            f"✓ Phone number verified: {mobile}"
        )

    return result


# =====================================================
# PHONE VERIFICATION STATUS
# =====================================================

@app.post("/phone-status")
async def phone_status(
    request: OTPRequest
):

    mobile = request.mobile.strip()

    return {
        "mobile": mobile,
        "verified": is_phone_verified(
            mobile
        )
    }


# =====================================================
# ANALYZE DOCUMENT
# =====================================================

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    selfie: UploadFile = File(...)
):

    print()
    print(
        "============================================================"
    )
    print("              VERISHIELD AI ANALYSIS")
    print(
        "============================================================"
    )

    # -------------------------------------------------
    # FILE PATHS
    # -------------------------------------------------

    document_path = (
        UPLOAD_DIR /
        file.filename
    )

    selfie_path = (
        UPLOAD_DIR /
        selfie.filename
    )

    # -------------------------------------------------
    # SAVE IDENTITY DOCUMENT
    # -------------------------------------------------

    print(
        "[0] Saving identity document..."
    )

    with open(
        document_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    print(
        "[0] Identity document saved."
    )

    # -------------------------------------------------
    # SAVE SELFIE
    # -------------------------------------------------

    print(
        "[0] Saving selfie..."
    )

    with open(
        selfie_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            selfie.file,
            buffer
        )

    print(
        "[0] Selfie saved."
    )

    # =================================================
    # 1. OCR
    # =================================================

    print()
    print(
        "[1] Starting OCR..."
    )

    try:

        extracted_text = extract_text(
            str(document_path)
        )

    except Exception as e:

        print(
            f"[1] OCR ERROR: {str(e)}"
        )

        extracted_text = ""

    print(
        "[1] OCR COMPLETE"
    )

    print(
        f"[1] Extracted characters: "
        f"{len(extracted_text)}"
    )

    # =================================================
    # 2. DOCUMENT FIELD EXTRACTION
    # =================================================

    print()
    print(
        "[2] Extracting document fields..."
    )

    try:

        fields = extract_fields(
            extracted_text
        )

    except Exception as e:

        print(
            f"[2] FIELD EXTRACTION ERROR: "
            f"{str(e)}"
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
        f"[2] Fields: {fields}"
    )

    # =================================================
    # 3. VALIDATION
    # =================================================

    print()
    print(
        "[3] Validating document..."
    )

    try:

        validation_issues = validate_fields(
            fields
        )

    except Exception as e:

        print(
            f"[3] VALIDATION ERROR: "
            f"{str(e)}"
        )

        validation_issues = [
            f"Validation failed: {str(e)}"
        ]

    print(
        f"[3] Validation: "
        f"{validation_issues}"
    )

    # =================================================
    # 4. TAMPERING DETECTION
    # =================================================

    print()
    print(
        "[4] Starting tampering detection..."
    )

    try:

        tampering = detect_tampering(
            str(document_path)
        )

    except Exception as e:

        print(
            f"[4] TAMPERING ERROR: "
            f"{str(e)}"
        )

        tampering = {
            "tampering_result": "UNKNOWN",
            "difference_score": 0,
            "message": str(e)
        }

    print(
        f"[4] Tampering: {tampering}"
    )

    # =================================================
    # 5. FACE DETECTION — ID
    # =================================================

    print()
    print(
        "[5] Detecting face on identity document..."
    )

    try:

        id_face_result = detect_face(
            str(document_path)
        )

    except Exception as e:

        print(
            f"[5] ID FACE ERROR: "
            f"{str(e)}"
        )

        id_face_result = {
            "face_detected": False,
            "face_count": 0,
            "message": str(e)
        }

    print(
        f"[5] ID face result: "
        f"{id_face_result}"
    )

    # =================================================
    # 6. FACE DETECTION — SELFIE
    # =================================================

    print()
    print(
        "[6] Detecting face in current selfie..."
    )

    try:

        selfie_face_result = detect_face(
            str(selfie_path)
        )

    except Exception as e:

        print(
            f"[6] SELFIE FACE ERROR: "
            f"{str(e)}"
        )

        selfie_face_result = {
            "face_detected": False,
            "face_count": 0,
            "message": str(e)
        }

    print(
        f"[6] Selfie face result: "
        f"{selfie_face_result}"
    )

    # =================================================
    # 7. FACE MATCHING
    # =================================================

    print()
    print(
        "[7] Starting face matching..."
    )

    try:

        face_match_result = match_faces(
            str(document_path),
            str(selfie_path)
        )

    except Exception as e:

        print(
            f"[7] FACE MATCHING ERROR: "
            f"{str(e)}"
        )

        face_match_result = {
            "match": False,
            "similarity_score": 0,
            "threshold": 0.363,
            "message": str(e),
            "id_faces_detected": 0,
            "selfie_faces_detected": 0
        }

    print(
        f"[7] Face matching complete:"
    )

    print(
        face_match_result
    )

    # =================================================
    # 8. RISK SCORING
    # =================================================

    print()
    print(
        "[8] Calculating risk score..."
    )

    risk_score = 0
    risk_factors = []

    # -------------------------------------------------
    # UNKNOWN DOCUMENT
    # -------------------------------------------------

    if fields.get(
        "document_type"
    ) == "UNKNOWN":

        risk_score += 10

        risk_factors.append(
            "Unable to identify document type"
        )

    # -------------------------------------------------
    # VALIDATION ISSUES
    # -------------------------------------------------

    for issue in validation_issues:

        risk_score += 20

        risk_factors.append(
            issue
        )

    # -------------------------------------------------
    # TAMPERING
    # -------------------------------------------------

    tampering_result = tampering.get(
        "tampering_result",
        "UNKNOWN"
    )

    if tampering_result == "SUSPICIOUS":

        risk_score += 30

        risk_factors.append(
            "Suspicious tampering indicators detected"
        )

    elif tampering_result == "HIGH RISK":

        risk_score += 60

        risk_factors.append(
            "High-risk tampering indicators detected"
        )

    # -------------------------------------------------
    # ID FACE
    # -------------------------------------------------

    if not id_face_result.get(
        "face_detected",
        False
    ):

        risk_score += 20

        risk_factors.append(
            "No face detected on identity document"
        )

    # -------------------------------------------------
    # SELFIE FACE
    # -------------------------------------------------

    if not selfie_face_result.get(
        "face_detected",
        False
    ):

        risk_score += 20

        risk_factors.append(
            "No face detected in current selfie"
        )

    # -------------------------------------------------
    # FACE MISMATCH
    # -------------------------------------------------

    if (
        id_face_result.get(
            "face_detected",
            False
        )
        and
        selfie_face_result.get(
            "face_detected",
            False
        )
    ):

        if not face_match_result.get(
            "match",
            False
        ):

            risk_score += 40

            risk_factors.append(
                "Identity document face does not match selfie"
            )

    # -------------------------------------------------
    # CAP SCORE
    # -------------------------------------------------

    risk_score = min(
        100,
        risk_score
    )

    # =================================================
    # FINAL STATUS
    # =================================================

    if risk_score >= 60:

        final_status = "HIGH RISK"

    elif risk_score >= 20:

        final_status = "SUSPICIOUS"

    else:

        final_status = "VERIFIED"

    # =================================================
    # LOG RESULTS
    # =================================================

    print()
    print(
        f"[8] Risk Score: "
        f"{risk_score}/100"
    )

    print(
        f"[8] Final Status: "
        f"{final_status}"
    )

    print(
        f"[8] Risk Factors: "
        f"{risk_factors}"
    )

    print()
    print(
        "============================================================"
    )
    print("                  ANALYSIS COMPLETE")
    print(
        "============================================================"
    )
    print()

    # =================================================
    # RESPONSE
    # =================================================

    return {

        "status": final_status,

        "risk_score": risk_score,

        "risk_factors": risk_factors,

        "document_fields": fields,

        "validation_issues": validation_issues,

        "tampering": tampering,

        "face_verification": id_face_result,

        "selfie_face_verification": selfie_face_result,

        "face_matching": face_match_result,

        "extracted_text": extracted_text

    }