import streamlit as st
import base64
import os
from openai import OpenAI 
import instructor
import requests
from pydantic.main import BaseModel
st.title("Koçtaş Ürün Bilgi Çıkarma")
st.image("koctas-output.png")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Product(BaseModel):
  UrunSınıfı: str
  UrunAdı: str
  UrunFiyatı: str
  UrunOzellikleri: str
  UrunDegerlendirme: str

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

koctas_image= st.file_uploader("Koçtaş Koçtaş Ürün Bilgi Çıkarma", type=["png", "jpg","jpeg"])
if koctas_image is not None and st.button('Özellikleri Çıkar'):
  st.image(koctas_image)
  with st.spinner('İşleniyor📈...'):
    base64_image = encode_image(koctas_image)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": """Görseldeki ürün hakkında detaylı billgi ver. Ürün sınıfı, ürün adı, ürün özellikleri, fiyatı, ve aldığı puanı yaz. Cevabı bir json formatı olarak döndür.
              """
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions",   headers=headers, json=payload)
    print(response)

    client = instructor.patch(OpenAI())

    response_json = response.json()
    content = response_json['choices'][0]['message']['content']

    urun_bilgisi = client.chat.completions.create(
      model="gpt-4",
      response_model=Product,
      messages=[
        {"role": "system", "content": "Sen ev aletleri sınıflandırıcısısın"},
        {"role": "user", "content": "Ürün sınıfı, ürün adı, fiyatı, ve aldığı puanı yaz. Cevabı bir json formatı olarak döndür. " + content}
      ]
    )
    resp_model = ''

    st.info(urun_bilgisi)