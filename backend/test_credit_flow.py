"""
Script de testing para verificar el flujo completo de créditos
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8002"
USER_EMAIL = "martingalant@gmail.com"
USER_PASSWORD = "tu_password_aqui"  # Martín deberá completar esto

def test_credit_flow():
    """Prueba el flujo completo de créditos"""

    print("=" * 60)
    print("🧪 TESTING CREDIT FLOW")
    print("=" * 60)

    # 1. Login para obtener token
    print("\n1️⃣ LOGIN...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        }
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return

    login_data = login_response.json()
    access_token = login_data.get("access_token")
    print(f"✅ Login successful")
    print(f"   Token: {access_token[:20]}...")

    # 2. Verificar balance inicial
    print("\n2️⃣ CHECKING BALANCE...")
    headers = {"Authorization": f"Bearer {access_token}"}

    balance_response = requests.get(
        f"{BASE_URL}/api/credits/balance",
        headers=headers
    )

    if balance_response.status_code != 200:
        print(f"❌ Balance check failed: {balance_response.text}")
        return

    balance_data = balance_response.json()
    initial_credits = balance_data.get("credits")
    print(f"✅ Current balance: {initial_credits} credits")

    # 3. Verificar historial
    print("\n3️⃣ CHECKING HISTORY...")
    history_response = requests.get(
        f"{BASE_URL}/api/credits/history",
        headers=headers
    )

    if history_response.status_code == 200:
        history_data = history_response.json()
        print(f"✅ Transaction history: {history_data.get('total_transactions')} transactions")
        if history_data.get('transactions'):
            print("\n   Recent transactions:")
            for tx in history_data['transactions'][:3]:
                print(f"   - {tx['type']}: {tx['credits_change']:+d} credits → {tx['credits_after']} total")

    print("\n" + "=" * 60)
    print("✅ CREDIT FLOW TEST COMPLETED")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   User: {USER_EMAIL}")
    print(f"   Credits: {initial_credits}")
    print(f"   Ready to process: {initial_credits} basic images or {initial_credits // 3} premium images")
    print("\n🎯 Next step: Process some images to test credit deduction!")

if __name__ == "__main__":
    test_credit_flow()
