import cv2


def detect_face(image_path):
    """
    Detect faces in an identity document image.
    """

    image = cv2.imread(image_path)

    if image is None:
        return {
            "face_detected": False,
            "face_count": 0,
            "message": "Unable to read image"
        }

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )

    return {
        "face_detected": len(faces) > 0,
        "face_count": len(faces),
        "message": (
            "Face detected successfully"
            if len(faces) > 0
            else "No face detected"
        )
    }