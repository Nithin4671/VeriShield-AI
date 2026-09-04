import cv2
import os


# ============================================================
# MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

DETECTION_MODEL = os.path.join(
    MODEL_DIR,
    "face_detection_yunet_2023mar.onnx"
)

RECOGNITION_MODEL = os.path.join(
    MODEL_DIR,
    "face_recognition_sface_2021dec.onnx"
)


# ============================================================
# FACE MATCHING THRESHOLD
# ============================================================

THRESHOLD = 0.363


# ============================================================
# CREATE FACE DETECTOR
# ============================================================

def get_detector():

    detector = cv2.FaceDetectorYN.create(
        DETECTION_MODEL,
        "",
        (320, 320),
        0.9,
        0.3,
        5000
    )

    return detector


# ============================================================
# DETECT FACES
# ============================================================

def detect_faces(image, detector):

    height, width = image.shape[:2]

    detector.setInputSize(
        (width, height)
    )

    _, faces = detector.detect(
        image
    )

    if faces is None:
        return []

    return faces


# ============================================================
# SELECT MAIN FACE
# ============================================================

def get_largest_face(faces):

    if len(faces) == 0:
        return None

    # YuNet face format:
    #
    # x
    # y
    # width
    # height
    # landmarks...
    #

    largest = max(
        faces,
        key=lambda face:
            float(face[2]) * float(face[3])
    )

    return largest


# ============================================================
# FACE MATCHING
# ============================================================

def match_faces(
    id_path,
    selfie_path
):

    print(
        "    → Loading identity document..."
    )

    id_image = cv2.imread(
        id_path
    )

    if id_image is None:

        return {
            "match": False,
            "similarity_score": 0,
            "threshold": THRESHOLD,
            "message":
                "Unable to read identity document",
            "id_faces_detected": 0,
            "selfie_faces_detected": 0
        }


    print(
        "    → Loading selfie..."
    )

    selfie_image = cv2.imread(
        selfie_path
    )

    if selfie_image is None:

        return {
            "match": False,
            "similarity_score": 0,
            "threshold": THRESHOLD,
            "message":
                "Unable to read selfie",
            "id_faces_detected": 0,
            "selfie_faces_detected": 0
        }


    # ========================================================
    # FACE DETECTOR
    # ========================================================

    print(
        "    → Loading face detector..."
    )

    detector = get_detector()


    # ========================================================
    # DETECT ID FACES
    # ========================================================

    print(
        "    → Detecting faces on identity document..."
    )

    id_faces = detect_faces(
        id_image,
        detector
    )

    print(
        f"    → Identity document faces detected: "
        f"{len(id_faces)}"
    )


    # ========================================================
    # DETECT SELFIE FACES
    # ========================================================

    print(
        "    → Detecting face in selfie..."
    )

    selfie_faces = detect_faces(
        selfie_image,
        detector
    )

    print(
        f"    → Selfie faces detected: "
        f"{len(selfie_faces)}"
    )


    # ========================================================
    # NO ID FACE
    # ========================================================

    if len(id_faces) == 0:

        return {
            "match": False,
            "similarity_score": 0,
            "threshold": THRESHOLD,
            "message":
                "No face detected on identity document",
            "id_faces_detected": 0,
            "selfie_faces_detected":
                len(selfie_faces)
        }


    # ========================================================
    # NO SELFIE FACE
    # ========================================================

    if len(selfie_faces) == 0:

        return {
            "match": False,
            "similarity_score": 0,
            "threshold": THRESHOLD,
            "message":
                "No face detected in selfie",
            "id_faces_detected":
                len(id_faces),
            "selfie_faces_detected": 0
        }


    # ========================================================
    # SELECT MAIN FACES
    # ========================================================

    print(
        "    → Selecting largest face from document..."
    )

    id_face = get_largest_face(
        id_faces
    )


    print(
        "    → Selecting largest face from selfie..."
    )

    selfie_face = get_largest_face(
        selfie_faces
    )


    # ========================================================
    # FACE RECOGNIZER
    # ========================================================

    print(
        "    → Loading face recognition model..."
    )

    recognizer = cv2.FaceRecognizerSF.create(
        RECOGNITION_MODEL,
        ""
    )


    # ========================================================
    # ALIGN ID FACE
    # ========================================================

    print(
        "    → Aligning identity document face..."
    )

    id_aligned = recognizer.alignCrop(
        id_image,
        id_face
    )


    # ========================================================
    # ALIGN SELFIE FACE
    # ========================================================

    print(
        "    → Aligning selfie face..."
    )

    selfie_aligned = recognizer.alignCrop(
        selfie_image,
        selfie_face
    )


    # ========================================================
    # EXTRACT ID FEATURES
    # ========================================================

    print(
        "    → Extracting identity face features..."
    )

    id_feature = recognizer.feature(
        id_aligned
    )


    # ========================================================
    # EXTRACT SELFIE FEATURES
    # ========================================================

    print(
        "    → Extracting selfie face features..."
    )

    selfie_feature = recognizer.feature(
        selfie_aligned
    )


    # ========================================================
    # COMPARE FEATURES
    # ========================================================

    print(
        "    → Comparing faces..."
    )

    score = recognizer.match(
        id_feature,
        selfie_feature,
        cv2.FaceRecognizerSF_FR_COSINE
    )

    score = float(score)


    # ========================================================
    # MATCH DECISION
    # ========================================================

    matched = (
        score >= THRESHOLD
    )


    print(
        f"    → Similarity score: "
        f"{score:.4f}"
    )

    print(
        f"    → Threshold: "
        f"{THRESHOLD}"
    )


    if matched:

        message = (
            "Faces appear to match"
        )

    else:

        message = (
            "Faces appear different"
        )


    # ========================================================
    # RESULT
    # ========================================================

    return {

        "match": matched,

        "similarity_score": round(
            score,
            4
        ),

        "threshold": THRESHOLD,

        "message": message,

        "id_faces_detected":
            len(id_faces),

        "selfie_faces_detected":
            len(selfie_faces)
    }