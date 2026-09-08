import os
import requests
from dotenv import load_dotenv

load_dotenv()

TWOFACTOR_API_KEY = os.getenv("TWOFACTOR_API_KEY")

OTP_TEMPLATE_NAME = "OTP1"

otp_store = {}


def send_otp(mobile):
    """
    Send a real SMS OTP using 2Factor AUTOGEN API.
    """

    if not TWOFACTOR_API_KEY:
        return {
            "success": False,
            "message": "2Factor API key is not configured."
        }

    mobile = mobile.strip()

    # 2Factor expects international format
    if len(mobile) == 10 and mobile.isdigit():
        phone_number = "+91" + mobile
    else:
        phone_number = mobile

    url = (
        f"https://2factor.in/API/V1/"
        f"{TWOFACTOR_API_KEY}/SMS/"
        f"{phone_number}/AUTOGEN/"
        f"{OTP_TEMPLATE_NAME}"
    )

    try:
        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        print()
        print("==========================================")
        print("2FACTOR OTP REQUEST")
        print(f"Mobile: {mobile}")
        print(f"Status: {data.get('Status')}")
        print("==========================================")
        print()

        if data.get("Status") != "Success":
            return {
                "success": False,
                "message": data.get(
                    "Details",
                    "Unable to send OTP."
                )
            }

        # Details contains the 2Factor session ID
        session_id = data.get("Details")

        otp_store[mobile] = {
            "session_id": session_id,
            "verified": False
        }

        return {
            "success": True,
            "message": "OTP sent successfully to your mobile.",
            "demo_mode": False
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"2Factor connection failed: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"OTP service error: {str(e)}"
        }


def verify_otp(mobile, otp):
    """
    Verify OTP using the 2Factor VERIFY API.
    """

    mobile = mobile.strip()

    record = otp_store.get(mobile)

    if not record:
        return {
            "success": False,
            "message": "No OTP found. Please request a new OTP."
        }

    session_id = record.get("session_id")

    if not session_id:
        return {
            "success": False,
            "message": "OTP session is missing. Please request a new OTP."
        }

    url = (
        f"https://2factor.in/API/V1/"
        f"{TWOFACTOR_API_KEY}/SMS/"
        f"VERIFY/"
        f"{session_id}/"
        f"{otp}"
    )

    try:
        response = requests.get(
            url,
            timeout=15
        )

        data = response.json()

        print()
        print("==========================================")
        print("2FACTOR OTP VERIFICATION")
        print(f"Mobile: {mobile}")
        print(f"Status: {data.get('Status')}")
        print("==========================================")
        print()

        if data.get("Status") == "Success":
            record["verified"] = True

            return {
                "success": True,
                "message": "Phone number verified successfully."
            }

        return {
            "success": False,
            "message": data.get(
                "Details",
                "Incorrect OTP."
            )
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "message": f"2Factor connection failed: {str(e)}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"OTP verification error: {str(e)}"
        }


def is_phone_verified(mobile):
    """
    Check whether the mobile number has been verified.
    """

    mobile = mobile.strip()

    record = otp_store.get(mobile)

    if not record:
        return False

    return record.get("verified", False)