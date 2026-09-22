import streamlit as st
import requests
import pandas as pd
from google import genai

# -------------------------
# GEMINI
# -------------------------

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)


# -------------------------
# SAYFA
# -------------------------

st.title("🍸 Türkiye Kokteyl & Mekan Bulucu")
st.write("Malzeme, mood ve şehrine göre kokteyl ve mekan bul!")


# -------------------------
# 81 İL
# -------------------------

sehirler = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya",
    "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur",
    "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum",
    "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari",
    "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir",
    "Kars", "Kastamonu", "Kayseri", "Kırklareli", "Kırşehir",
    "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa",
    "Kahramanmaraş", "Mardin", "Muğla", "Muş", "Nevşehir",
    "Niğde", "Ordu", "Rize", "Sakarya", "Samsun",
    "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van",
    "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan",
    "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye",
    "Düzce"
]


# -------------------------
# KULLANICI GİRİŞLERİ
# -------------------------

malzeme = st.text_input(
    "🍹 Hangi malzemeyi istiyorsun?",
    placeholder="Örnek: vodka, gin, rum"
)

mood = st.text_input(
    "😎 Nasıl bir ortam istiyorsun?",
    placeholder="Örnek: sakin, eğlenceli, romantik"
)

sehir = st.selectbox(
    "📍 Hangi şehirdesin?",
    sehirler,
    index=sehirler.index("Samsun")
)


# -------------------------
# BUTON
# -------------------------

if st.button("🔍 Kokteyl ve Mekan Bul"):

    if not malzeme:
        st.warning("⚠️ Önce bir malzeme yaz!")

    elif not mood:
        st.warning("⚠️ Moodunu yaz!")

    else:

        # -------------------------
        # COCKTAIL DB
        # -------------------------

        st.info("🍹 Kokteyller aranıyor...")

        try:

            response = requests.get(
                "https://www.thecocktaildb.com/api/json/v1/1/filter.php",
                params={"i": malzeme.strip()},
                timeout=10
            )

            response.raise_for_status()

            veri = response.json()

            kokteyller = veri.get("drinks")

            if not isinstance(kokteyller, list):

                st.error(
                    f"❌ '{malzeme}' ile kokteyl bulunamadı."
                )

                st.stop()

            kokteyl_isimleri = [
                k["strDrink"]
                for k in kokteyller[:10]
            ]

            st.success("🍸 Kokteyller bulundu!")

            st.write(
                "Bulunan kokteyller:",
                kokteyl_isimleri
            )


            # -------------------------
            # GEMINI
            # -------------------------

            st.info("🤖 Yapay zeka, istediğin ortama göre kokteyl seçiyor...")

            prompt = f"""
            Kullanıcının istediği malzeme: {malzeme}
            Kullanıcının moodu: {mood}

            Bulunan kokteyller:
            {kokteyl_isimleri}

            Bu kokteyller arasından mooda en uygun
            en fazla 3 kokteyli seç.

            Türkçe cevap ver.

            Her kokteyl için:
            - kokteyl adı
            - neden uygun olduğu

            Kısa ve anlaşılır yaz.
            """

            try:
                gemini_cevap = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )

                st.subheader("🤖 Yapay Zeka Kokteyl Önerisi")
                st.write(gemini_cevap.text)

            except Exception:
                st.warning(
                    "⚠️ Gemini şu an yoğun. Kokteyl önerisi atlandı, mekan aramasına devam ediliyor."
                )

            # -------------------------
            # OPENSTREETMAP MEKAN ARAMA
            # -------------------------

            st.info(f"📍 {sehir} içindeki mekanlar aranıyor...")

            # Önce şehrin koordinat/sınır bilgisini bul
            sehir_response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": f"{sehir}, Türkiye",
                    "format": "jsonv2",
                    "limit": 1,
                    "countrycodes": "tr"
                },
                headers={
                    "User-Agent": "KokteylMekanBulucu/1.0"
                },
                timeout=10
            )

            sehir_response.raise_for_status()
            sehir_sonuc = sehir_response.json()

            mekanlar = []

            if sehir_sonuc:

                lat = float(sehir_sonuc[0]["lat"])
                lon = float(sehir_sonuc[0]["lon"])

                overpass_sorgu = f"""
                [out:json][timeout:25];

                (
                  nwr["amenity"~"^(bar|pub|nightclub|biergarten)$"](around:25000,{lat},{lon});
                  nwr["amenity"~"^(restaurant|cafe)$"]["bar"="yes"](around:25000,{lat},{lon});
                  nwr["amenity"~"^(restaurant|cafe)$"](around:15000,{lat},{lon});
                );

                out center tags;
                """

                overpass_response = requests.get(
                    "https://overpass-api.de/api/interpreter",
                    params={
                        "data": overpass_sorgu
                    },
                    headers={
                        "User-Agent": "KokteylMekanBulucu/1.0",
                        "Accept": "application/json"
                    },
                    timeout=30
                )

                overpass_response.raise_for_status()

                overpass_veri = overpass_response.json()

                for yer in overpass_veri.get("elements", []):

                    tags = yer.get("tags", {})
                    isim = tags.get("name")

                    if not isim:
                        continue

                    # Node ise koordinat direkt burada
                    yer_lat = yer.get("lat")
                    yer_lon = yer.get("lon")

                    # Way / relation ise koordinat center içinde
                    if yer_lat is None or yer_lon is None:
                        center = yer.get("center", {})
                        yer_lat = center.get("lat")
                        yer_lon = center.get("lon")

                    if yer_lat is None or yer_lon is None:
                        continue

                    tur = tags.get("amenity", "mekan")

                    # Mekanı kokteyl/gece ortamına göre puanla
                    puan = 0

                    if tur == "bar":
                        puan += 100
                    elif tur == "pub":
                        puan += 90
                    elif tur == "nightclub":
                        puan += 85
                    elif tur == "biergarten":
                        puan += 80

                    if tags.get("bar") == "yes":
                        puan += 70

                    if tags.get("cocktails") == "yes":
                        puan += 80

                    if tags.get("alcohol") == "yes":
                        puan += 40

                    isim_kucuk = isim.lower()

                    anahtar_kelimeler = [
                        "bar", "pub", "lounge", "club",
                        "cocktail", "roof", "teras",
                        "gastropub", "bistro"
                    ]

                    for kelime in anahtar_kelimeler:
                        if kelime in isim_kucuk:
                            puan += 30

                    mekanlar.append({
                        "isim": isim,
                        "adres": tags.get(
                            "addr:street",
                            f"{sehir}, Türkiye"
                        ),
                        "lat": yer_lat,
                        "lon": yer_lon,
                        "tur": tur,
                        "puan": puan
                    })

            # -------------------------
            # MEKANLARI GÖSTER
            # -------------------------

                if mekanlar:
                    uygun_mekanlar = [
                        m for m in mekanlar
                        if m["puan"] > 0
                    ]

                    mekanlar = sorted(
                        uygun_mekanlar,
                        key=lambda x: x["puan"],
                        reverse=True
                    )[:10]

                st.success(
                    f"📍 {len(mekanlar)} mekan bulundu!"
                )

                st.subheader(
                    f"🍸 {sehir} Mekanları"
                )

                for mekan in mekanlar:

                    st.write(
                        f"### 📍 {mekan['isim']}"
                    )

                    st.caption(
                        mekan["adres"]
                    )


                # -------------------------
                # HARİTA
                # -------------------------

                st.subheader("🗺️ Harita")

                harita_verisi = pd.DataFrame(
                    [
                        {
                            "lat": m["lat"],
                            "lon": m["lon"]
                        }
                        for m in mekanlar
                    ]
                )

                st.map(harita_verisi)

                st.caption(
                    "Mekan verileri © OpenStreetMap contributors"
                )

            else:

                st.warning(
                    f"⚠️ {sehir} için uygun mekan bulunamadı."
                )


        except requests.RequestException as hata:

            st.error("❌ İnternet/API bağlantı hatası:")

            st.write(hata)


        except Exception as hata:

            st.error("❌ Bir hata oluştu:")

            st.exception(hata)