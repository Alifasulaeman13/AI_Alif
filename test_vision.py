import google.generativeai as genai
import base64

# Konfigurasi API Key
genai.configure(api_key="AIzaSyBt3RA9JK7KLOSJeC05q-gKxbzrQmsGB8c")

print("🔄 Testing model vision...")
print("=" * 50)

try:
    # Test vision model
    vision_model = genai.GenerativeModel("models/gemini-2.5-flash-image")
    print("✅ Model vision berhasil dibuat")
    
    # Test dengan gambar kecil (base64 placeholder)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    print("🔄 Testing generate content dengan gambar...")
    image_part = {
        "mime_type": "image/png",
        "data": base64.b64decode(test_image)
    }
    
    response = vision_model.generate_content(["test", image_part])
    print("✅ Generate content berhasil:")
    print(f"Response: {response.text[:100]}...")
    
except Exception as e:
    print(f"❌ Error detail:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
    
    # Cek apakah ini quota error atau model error
    error_msg = str(e).lower()
    if "quota" in error_msg or "429" in error_msg:
        print("\n📊 Ini adalah error kuota")
    elif "not found" in error_msg or "404" in error_msg:
        print("\n📊 Model tidak ditemukan")
    else:
        print(f"\n📊 Error lain: {error_msg}")