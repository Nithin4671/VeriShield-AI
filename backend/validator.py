import re
from datetime import datetime


def detect_document_type(text):
    text_upper = text.upper()

    if (
        "AADHAAR" in text_upper
        or "GOVERNMENT OF INDIA" in text_upper
        or re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)
    ):
        return "AADHAAR"

    if "CAYMAN ISLANDS" in text_upper:
        return "CAYMAN_ID"

    if "IDENTITY CARD" in text_upper or "ID CARD" in text_upper:
        return "GENERIC_ID"

    return "UNKNOWN"


def clean_name(name):
    name = name.strip()

    # Remove OCR garbage at the beginning/end
    name = re.sub(
        r"[^A-Za-z .'-]",
        "",
        name
    )

    # Normalize spaces
    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    return name


def is_possible_name(text):

    if not text:
        return False

    text = clean_name(text)

    if not text:
        return False

    upper = text.upper()

    # Reject common document/OCR words
    rejected_words = [
        "GOVERNMENT",
        "INDIA",
        "AADHAAR",
        "UIDAI",
        "DOB",
        "DATE",
        "BIRTH",
        "MALE",
        "FEMALE",
        "TRANSGENDER",
        "YEAR",
        "ADDRESS",
        "IDENTIFICATION",
        "CARD",
        "PROOF",
        "CITIZENSHIP",
        "NAME"
    ]

    for word in rejected_words:
        if word in upper:
            return False

    # Names should not contain numbers
    if re.search(r"\d", text):
        return False

    words = text.split()

    # We expect at least first + last name
    if len(words) < 2:
        return False

    # Avoid very long OCR sentences
    if len(words) > 5:
        return False

    for word in words:

        if not re.fullmatch(
            r"[A-Za-z][A-Za-z.'-]*",
            word
        ):
            return False

    return True


def extract_aadhaar_name(text):

    # =========================================================
    # METHOD 1
    # Explicit "Name : ..."
    # =========================================================

    match = re.search(
        r"\bName\s*[:\-]\s*"
        r"([A-Za-z][A-Za-z .'-]+)",
        text,
        re.IGNORECASE
    )

    if match:

        name = clean_name(
            match.group(1)
        )

        name = re.split(
            r"\b(?:DOB|Date\s*of\s*Birth|Male|Female|Transgender)\b",
            name,
            flags=re.IGNORECASE
        )[0].strip()

        if is_possible_name(name):
            return name

    # =========================================================
    # METHOD 2
    # OCR variations of "Name"
    # =========================================================

    match = re.search(
        r"\b(?:Nam|Nane|Narne|Narne)\s*[:\-]\s*"
        r"([A-Za-z][A-Za-z .'-]+)",
        text,
        re.IGNORECASE
    )

    if match:

        name = clean_name(
            match.group(1)
        )

        name = re.split(
            r"\b(?:DOB|Date\s*of\s*Birth|Male|Female|Transgender)\b",
            name,
            flags=re.IGNORECASE
        )[0].strip()

        if is_possible_name(name):
            return name

    # =========================================================
    # METHOD 3
    # Search several lines before DOB
    #
    # This handles your Aadhaar:
    #
    # Nithin R
    #
    # [OCR noise]
    #
    # DOB : 29/09/2006
    # =========================================================

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for i, line in enumerate(lines):

        if re.search(
            r"(?:DOB|Date\s*of\s*Birth)",
            line,
            re.IGNORECASE
        ):

            # Search up to 6 previous OCR lines
            start = max(
                0,
                i - 6
            )

            candidates = lines[start:i]

            # Search from closest to furthest
            for candidate in reversed(candidates):

                candidate = clean_name(
                    candidate
                )

                if is_possible_name(candidate):
                    return candidate

    # =========================================================
    # METHOD 4
    # Look for a name-like line anywhere in the OCR
    # =========================================================

    for line in lines:

        candidate = clean_name(line)

        if is_possible_name(candidate):

            # Don't accidentally return something that looks
            # like a document number or unrelated text
            if len(candidate) <= 40:
                return candidate

    return None


def extract_fields(text):

    document_type = detect_document_type(text)

    fields = {
        "document_type": document_type,
        "document_number": None,
        "name": None,
        "date_of_birth": None,
        "gender": None,
        "nationality": None,
        "date_of_issue": None,
        "date_of_expiry": None
    }

    # =========================================================
    # AADHAAR
    # =========================================================

    if document_type == "AADHAAR":

        # Aadhaar number
        match = re.search(
            r"\b\d{4}\s?\d{4}\s?\d{4}\b",
            text
        )

        if match:

            fields["document_number"] = re.sub(
                r"\s+",
                " ",
                match.group(0)
            ).strip()

        # Name
        fields["name"] = extract_aadhaar_name(text)

        # DOB
        match = re.search(
            r"(?:Date\s*of\s*Birth|DOB|fafa|faf)"
            r"\s*[:\-]?\s*"
            r"([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})",
            text,
            re.IGNORECASE
        )

        if match:

            fields["date_of_birth"] = (
                match.group(1).strip()
            )

        # DOB fallback
        if not fields["date_of_birth"]:

            dates = re.findall(
                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
                text
            )

            if dates:
                fields["date_of_birth"] = dates[0]

        # Gender
        match = re.search(
            r"\b(FEMALE|MALE|TRANSGENDER)\b",
            text,
            re.IGNORECASE
        )

        if match:

            fields["gender"] = (
                match.group(1).upper()
            )

        return fields

    # =========================================================
    # GENERIC / CAYMAN ID
    # =========================================================

    match = re.search(
        r"DOCUMENT\s*NUMBER\s*[:\-]?\s*([0-9A-Z ]+)",
        text,
        re.IGNORECASE
    )

    if match:
        fields["document_number"] = (
            match.group(1).strip()
        )

    match = re.search(
        r"GIVEN\s*NAMES\s*[:\-]?\s*([A-Za-z ]+)",
        text,
        re.IGNORECASE
    )

    if match:
        fields["name"] = (
            match.group(1).strip()
        )

    match = re.search(
        r"DATE\s*OF\s*BIRTH\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        fields["date_of_birth"] = (
            match.group(1).strip()
        )

    match = re.search(
        r"\b(CAYMANIAN|INDIAN|BRITISH|AMERICAN|CANADIAN)\b",
        text,
        re.IGNORECASE
    )

    if match:
        fields["nationality"] = (
            match.group(1).upper()
        )

    match = re.search(
        r"DATE\s*OF\s*ISSUE\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        fields["date_of_issue"] = (
            match.group(1).strip()
        )

    match = re.search(
        r"DATE\s*OF\s*EXPIRY\s*[:\-]?\s*(.+)",
        text,
        re.IGNORECASE
    )

    if match:
        fields["date_of_expiry"] = (
            match.group(1).strip()
        )

    return fields


def parse_date(date_string):

    if not date_string:
        return None

    cleaned = (
        date_string
        .strip()
        .replace("Sept", "Sep")
    )

    formats = [
        "%d %b %Y",
        "%d %B %Y",
        "%d/%m/%Y",
        "%d-%m-%Y"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                cleaned,
                fmt
            )

        except ValueError:
            continue

    return None


def validate_fields(fields):

    issues = []

    document_type = fields.get(
        "document_type",
        "UNKNOWN"
    )

    if document_type == "UNKNOWN":

        issues.append(
            "Unable to identify document type"
        )

        return issues

    # =========================================================
    # AADHAAR
    # =========================================================

    if document_type == "AADHAAR":

        if not fields.get("document_number"):

            issues.append(
                "Aadhaar number could not be extracted"
            )

        # Missing name is treated as an OCR limitation,
        # not automatically as fraud.

        if not fields.get("date_of_birth"):

            issues.append(
                "Date of birth could not be extracted"
            )

        if not fields.get("gender"):

            issues.append(
                "Gender could not be extracted"
            )

        number = fields.get(
            "document_number"
        )

        if number:

            digits = re.sub(
                r"\D",
                "",
                number
            )

            if len(digits) != 12:

                issues.append(
                    "Invalid Aadhaar number format"
                )

        dob = parse_date(
            fields.get("date_of_birth")
        )

        if (
            fields.get("date_of_birth")
            and dob is None
        ):

            issues.append(
                "Invalid date of birth format"
            )

        return issues

    # =========================================================
    # GENERIC DOCUMENT
    # =========================================================

    if not fields.get("document_number"):

        issues.append(
            "Document number missing"
        )

    if not fields.get("date_of_issue"):

        issues.append(
            "Date of issue missing"
        )

    if not fields.get("date_of_expiry"):

        issues.append(
            "Date of expiry missing"
        )

    if not fields.get("date_of_expiry"):

        return issues

    expiry_date = parse_date(
        fields["date_of_expiry"]
    )

    if expiry_date is None:

        issues.append(
            "Invalid expiry date format"
        )

        return issues

    today = datetime.now()

    if expiry_date < today:

        issues.append(
            "Document has expired"
        )

    if fields.get("date_of_issue"):

        issue_date = parse_date(
            fields["date_of_issue"]
        )

        if issue_date is None:

            issues.append(
                "Invalid issue date format"
            )

        else:

            if issue_date > today:

                issues.append(
                    "Issue date is in the future"
                )

            if expiry_date <= issue_date:

                issues.append(
                    "Expiry date must be after issue date"
                )

    return issues