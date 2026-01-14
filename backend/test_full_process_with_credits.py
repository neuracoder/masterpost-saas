"""
Test completo: Upload → Process → Verify credit deduction
"""

import requests
import json
import time
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8002"
USER_EMAIL = "martingalant@gmail.com"
USER_PASSWORD = "tu_password_aqui"  # Martín deberá completar esto

def test_full_process():
    """Prueba el flujo completo: upload, process, credit deduction"""

    print("=" * 80)
    print("🧪 FULL PROCESS TEST WITH CREDITS")
    print("=" * 80)

    # 1. Login
    print("\n1️⃣ LOGIN...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": USER_EMAIL, "password": USER_PASSWORD}
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return

    access_token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"✅ Login successful")

    # 2. Check initial balance
    print("\n2️⃣ CHECKING INITIAL BALANCE...")
    balance_response = requests.get(f"{BASE_URL}/api/credits/balance", headers=headers)
    initial_balance = balance_response.json().get("credits")
    print(f"✅ Initial balance: {initial_balance} credits")

    # 3. Find test images
    print("\n3️⃣ FINDING TEST IMAGES...")
    test_dir = Path("test_images")
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        print(f"   Please create {test_dir} and add some test images")
        return

    image_files = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
    if not image_files:
        print(f"❌ No images found in {test_dir}")
        return

    # Use only first 2 images for testing
    test_images = image_files[:2]
    print(f"✅ Found {len(image_files)} images, using {len(test_images)} for test")

    # 4. Upload images
    print("\n4️⃣ UPLOADING IMAGES...")
    files = []
    for img_path in test_images:
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/jpeg')))

    upload_response = requests.post(
        f"{BASE_URL}/api/v1/upload",
        files=files,
        headers=headers
    )

    if upload_response.status_code != 200:
        print(f"❌ Upload failed: {upload_response.text}")
        return

    upload_data = upload_response.json()
    job_id = upload_data.get("job_id")
    print(f"✅ Upload successful")
    print(f"   Job ID: {job_id}")
    print(f"   Images uploaded: {upload_data.get('images_found')}")

    # 5. Calculate credits needed
    use_premium = False  # Change to True to test premium processing
    credits_per_image = 3 if use_premium else 1
    images_count = len(test_images)
    credits_needed = credits_per_image * images_count

    print(f"\n📊 CREDIT CALCULATION:")
    print(f"   Processing mode: {'PREMIUM (Qwen)' if use_premium else 'BASIC (rembg)'}")
    print(f"   Images to process: {images_count}")
    print(f"   Credits per image: {credits_per_image}")
    print(f"   Total credits needed: {credits_needed}")
    print(f"   Current balance: {initial_balance}")

    if initial_balance < credits_needed:
        print(f"\n❌ INSUFFICIENT CREDITS!")
        print(f"   You have: {initial_balance} credits")
        print(f"   You need: {credits_needed} credits")
        print(f"   Shortfall: {credits_needed - initial_balance} credits")
        return

    print(f"   ✅ Sufficient credits!")
    print(f"   Balance after: {initial_balance - credits_needed} credits")

    # 6. Process images
    print("\n5️⃣ PROCESSING IMAGES...")
    process_response = requests.post(
        f"{BASE_URL}/api/v1/process",
        json={
            "job_id": job_id,
            "pipeline": "amazon",
            "settings": {
                "use_premium": use_premium,
                "shadow_enabled": False
            }
        },
        headers=headers
    )

    if process_response.status_code == 402:
        print(f"❌ INSUFFICIENT CREDITS (as expected if testing)")
        print(f"   Response: {process_response.json()}")
        return
    elif process_response.status_code != 200:
        print(f"❌ Process failed: {process_response.text}")
        return

    process_data = process_response.json()
    print(f"✅ Processing started")
    print(f"   Status: {process_data.get('status')}")
    print(f"   Credits will be deducted: {process_data.get('total_credits')}")

    # 7. Wait for processing to complete
    print("\n6️⃣ WAITING FOR PROCESSING TO COMPLETE...")
    max_attempts = 30
    for i in range(max_attempts):
        time.sleep(2)
        status_response = requests.get(
            f"{BASE_URL}/api/v1/status/{job_id}",
            headers=headers
        )

        if status_response.status_code == 200:
            status_data = status_response.json()
            current_status = status_data.get("status")

            print(f"   Attempt {i+1}/{max_attempts}: {current_status}")

            if current_status == "completed":
                print(f"✅ Processing completed!")
                print(f"   Success: {status_data.get('success')}")
                print(f"   Failed: {status_data.get('failed')}")
                break
            elif current_status == "failed":
                print(f"❌ Processing failed!")
                break

    # 8. Check final balance
    print("\n7️⃣ CHECKING FINAL BALANCE...")
    time.sleep(2)  # Wait for credit deduction to complete

    final_balance_response = requests.get(f"{BASE_URL}/api/credits/balance", headers=headers)
    final_balance = final_balance_response.json().get("credits")

    print(f"✅ Final balance: {final_balance} credits")

    # 9. Verify credit deduction
    print("\n8️⃣ VERIFYING CREDIT DEDUCTION...")
    expected_balance = initial_balance - credits_needed
    actual_deduction = initial_balance - final_balance

    print(f"\n📊 CREDIT DEDUCTION SUMMARY:")
    print(f"   Initial balance: {initial_balance} credits")
    print(f"   Expected deduction: {credits_needed} credits")
    print(f"   Actual deduction: {actual_deduction} credits")
    print(f"   Final balance: {final_balance} credits")

    if actual_deduction == credits_needed:
        print(f"\n✅ CREDIT DEDUCTION VERIFIED!")
    else:
        print(f"\n⚠️  CREDIT DEDUCTION MISMATCH!")
        print(f"   Expected: {credits_needed}")
        print(f"   Actual: {actual_deduction}")

    # 10. Check transaction history
    print("\n9️⃣ CHECKING TRANSACTION HISTORY...")
    history_response = requests.get(f"{BASE_URL}/api/credits/history", headers=headers)
    history_data = history_response.json()

    print(f"✅ Recent transactions:")
    for tx in history_data['transactions'][:3]:
        print(f"   - {tx['type']}: {tx['credits_change']:+d} credits → {tx['credits_after']} total")
        print(f"     {tx['description']}")
        print(f"     {tx['created_at']}")

    print("\n" + "=" * 80)
    print("✅ FULL PROCESS TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_full_process()
