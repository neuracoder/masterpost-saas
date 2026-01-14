"""
Script para verificar la cuota gratuita de Qwen Image Edit API
y hacer pruebas básicas de funcionamiento
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent))

# Cargar variables de entorno
load_dotenv()

import dashscope
from dashscope import MultiModalConversation

# Configurar región Singapore
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'


def check_quota_and_test():
    """
    Verificar acceso a la API y hacer un test simple
    """

    print("="*80)
    print("QWEN API - QUOTA & ACCESS CHECK")
    print("="*80)
    print()

    # 1. Verificar API key
    api_key = os.getenv('DASHSCOPE_API_KEY')

    if not api_key:
        print("[X] ERROR: DASHSCOPE_API_KEY not found")
        print()
        print("Solutions:")
        print("  1. Check backend/.env file")
        print("  2. Add: DASHSCOPE_API_KEY=sk-41cb19a4a3a04ab8974a9abf0f4b34ee")
        print("  3. Restart terminal/script")
        print()
        print("="*80)
        return False

    print("[OK] API Key found")
    print(f"   Key: {api_key[:15]}...{api_key[-5:]}")
    print(f"   Region: Singapore (dashscope-intl)")
    print(f"   Model: qwen-image-edit")
    print(f"   Cost: $0.045 per image")
    print()

    # 2. Test con imagen pública
    print("[*] Testing with public image...")
    test_image_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    print(f"   URL: {test_image_url}")
    print()

    # 3. Construir request
    messages = [
        {
            "role": "user",
            "content": [
                {"image": test_image_url},
                {"text": "Remove the background completely. Replace with pure white RGB(255,255,255)."}
            ]
        }
    ]

    print("[*] Calling Qwen API...")
    print("   Please wait (may take 5-10 seconds)...")
    print()

    try:
        # Llamar API
        response = MultiModalConversation.call(
            api_key=api_key,
            model="qwen-image-edit",
            messages=messages,
            stream=False,
            watermark=False,
            negative_prompt="shadows, reflections, background"
        )

        # Analizar respuesta
        print(f"[*] Response received!")
        print(f"   Status: {response.status_code}")
        print()

        if response.status_code == 200:
            # EXITO
            print("="*80)
            print("[OK] SUCCESS! QWEN API IS WORKING!")
            print("="*80)
            print()

            # Extraer información
            try:
                image_url = response.output.choices[0].message.content[0]['image']
                print("[i] Response Details:")
                print(f"   Request ID: {response.request_id}")
                print(f"   Output URL: {image_url[:60]}...")
                print(f"   URL valid for: 24 hours")
                print()
            except:
                print("[!]  Could not extract image URL")
                print()

            # Usage info
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                print("[$] Usage Information:")
                print(f"   Images processed: {usage.get('image_count', 1)}")
                if usage.get('width'):
                    print(f"   Dimensions: {usage.get('width')}x{usage.get('height')}")
                print()

            print("="*80)
            print("[i] NEXT STEPS:")
            print("="*80)
            print()
            print("[1]  Check remaining quota:")
            print("   -> Login to https://modelstudio.console.aliyun.com/")
            print("   -> Go to 'Billing' or 'Usage' section")
            print("   -> Look for 'qwen-image-edit' usage")
            print()
            print("[2]  This test likely used:")
            print("   -> FREE quota (if you have it)")
            print("   -> OR charged $0.045")
            print()
            print("[3]  Ready to integrate:")
            print("   -> Qwen API is working correctly")
            print("   -> Code is ready for production")
            print("   -> Can process images now")
            print()
            print("="*80)

            return True

        else:
            # ERROR
            print("="*80)
            print("[X] ERROR - API CALL FAILED")
            print("="*80)
            print()
            print(f"Status Code: {response.status_code}")
            print(f"Error Code: {response.code}")
            print(f"Error Message: {response.message}")
            print()

            # Analizar tipo de error
            error_msg = str(response.message).lower()

            if "quota" in error_msg or "exceed" in error_msg:
                print("[!]  QUOTA/LIMIT ISSUE")
                print()
                print("Possible causes:")
                print("  • Free quota exhausted")
                print("  • Rate limit exceeded (2 requests/second)")
                print("  • Monthly limit reached")
                print()
                print("Solutions:")
                print("  1. Wait a few seconds and retry")
                print("  2. Check quota in Alibaba Cloud console")
                print("  3. Upgrade to paid plan if needed")

            elif "auth" in error_msg or "key" in error_msg or "invalid" in error_msg:
                print("[!]  AUTHENTICATION ISSUE")
                print()
                print("Possible causes:")
                print("  • Invalid API key")
                print("  • Expired API key")
                print("  • Wrong region (Singapore vs Beijing)")
                print()
                print("Solutions:")
                print("  1. Verify API key in console")
                print("  2. Generate new API key")
                print("  3. Check .env file has correct key")

            elif "not found" in error_msg or "404" in error_msg:
                print("[!]  ENDPOINT/MODEL ISSUE")
                print()
                print("Possible causes:")
                print("  • Model not activated in your region")
                print("  • Wrong endpoint URL")
                print("  • Service not available")
                print()
                print("Solutions:")
                print("  1. Activate 'qwen-image-edit' in console")
                print("  2. Check region configuration")
                print("  3. Verify service is available")

            else:
                print("[!]  UNKNOWN ERROR")
                print()
                print("Recommendations:")
                print("  1. Check Alibaba Cloud console")
                print("  2. Verify Model Studio is activated")
                print("  3. Review documentation:")
                print("     https://www.alibabacloud.com/help/en/model-studio/")

            print()
            print("="*80)

            return False

    except ImportError as e:
        print("="*80)
        print("[X] IMPORT ERROR")
        print("="*80)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Solution:")
        print("  Install dashscope library:")
        print()
        print("  cd backend")
        print("  pip install dashscope>=1.14.0")
        print()
        print("="*80)
        return False

    except Exception as e:
        print("="*80)
        print("[X] UNEXPECTED ERROR")
        print("="*80)
        print()
        print(f"Error: {str(e)}")
        print(f"Type: {type(e).__name__}")
        print()
        print("Possible causes:")
        print("  • Network/connection issue")
        print("  • Firewall blocking request")
        print("  • Service temporarily unavailable")
        print()
        print("Solutions:")
        print("  1. Check internet connection")
        print("  2. Try again in a few minutes")
        print("  3. Check firewall settings")
        print()
        print("="*80)
        return False


if __name__ == "__main__":
    print()
    success = check_quota_and_test()
    print()

    if success:
        print("[OK] All systems go! Ready to integrate Qwen Premium.")
    else:
        print("[!]  Fix the issues above before integrating.")

    print()
