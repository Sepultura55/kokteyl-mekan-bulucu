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
sehir_koordinatlari = {
    "Adana": (37.0000, 35.3213),
    "Adıyaman": (37.7648, 38.2786),
    "Afyonkarahisar": (38.7507, 30.5567),
    "Ağrı": (39.7191, 43.0503),
    "Amasya": (40.6499, 35.8353),
    "Ankara": (39.9334, 32.8597),
    "Antalya": (36.8969, 30.7133),
    "Artvin": (41.1828, 41.8183),
    "Aydın": (37.8560, 27.8416),
    "Balıkesir": (39.6484, 27.8826),
    "Bilecik": (40.0567, 30.0665),
    "Bingöl": (38.8854, 40.4966),
    "Bitlis": (38.4006, 42.1095),
    "Bolu": (40.7395, 31.6116),
    "Burdur": (37.7203, 30.2908),
    "Bursa": (40.1885, 29.0610),
    "Çanakkale": (40.1553, 26.4142),
    "Çankırı": (40.6013, 33.6134),
    "Çorum": (40.5506, 34.9556),
    "Denizli": (37.7765, 29.0864),
    "Diyarbakır": (37.9144, 40.2306),
    "Edirne": (41.6771, 26.5557),
    "Elazığ": (38.6810, 39.2264),
    "Erzincan": (39.7500, 39.5000),
    "Erzurum": (39.9000, 41.2700),
    "Eskişehir": (39.7767, 30.5206),
    "Gaziantep": (37.0662, 37.3833),
    "Giresun": (40.9128, 38.3895),
    "Gümüşhane": (40.4386, 39.5086),
    "Hakkari": (37.5744, 43.7408),
    "Hatay": (36.2023, 36.1600),
    "Isparta": (37.7648, 30.5566),
    "Mersin": (36.8121, 34.6415),
    "İstanbul": (41.0082, 28.9784),
    "İzmir": (38.4237, 27.1428),
    "Kars": (40.6013, 43.0975),
    "Kastamonu": (41.3887, 33.7827),
    "Kayseri": (38.7312, 35.4787),
    "Kırklareli": (41.7351, 27.2252),
    "Kırşehir": (39.1425, 34.1709),
    "Kocaeli": (40.7654, 29.9408),
    "Konya": (37.8746, 32.4932),
    "Kütahya": (39.4167, 29.9833),
    "Malatya": (38.3552, 38.3095),
    "Manisa": (38.6191, 27.4289),
    "Kahramanmaraş": (37.5858, 36.9371),
    "Mardin": (37.3212, 40.7245),
    "Muğla": (37.2153, 28.3636),
    "Muş": (38.9462, 41.7539),
    "Nevşehir": (38.6939, 34.6857),
    "Niğde": (37.9667, 34.6833),
    "Ordu": (40.9839, 37.8764),
    "Rize": (41.0201, 40.5234),
    "Sakarya": (40.7731, 30.3948),
    "Samsun": (41.2867, 36.3300),
    "Siirt": (37.9333, 41.9500),
    "Sinop": (42.0231, 35.1531),
    "Sivas": (39.7477, 37.0179),
    "Tekirdağ": (40.9780, 27.5110),
    "Tokat": (40.3167, 36.5500),
    "Trabzon": (41.0015, 39.7178),
    "Tunceli": (39.1079, 39.5401),
    "Şanlıurfa": (37.1674, 38.7955),
    "Uşak": (38.6823, 29.4082),
    "Van": (38.4891, 43.4089),
    "Yozgat": (39.8181, 34.8147),
    "Zonguldak": (41.4564, 31.7987),
    "Aksaray": (38.3687, 34.0370),
    "Bayburt": (40.2552, 40.2249),
    "Karaman": (37.1759, 33.2287),
    "Kırıkkale": (39.8468, 33.5153),
    "Batman": (37.8812, 41.1351),
    "Şırnak": (37.4187, 42.4918),
    "Bartın": (41.6344, 32.3375),
    "Ardahan": (41.1105, 42.7022),
    "Iğdır": (39.9237, 44.0450),
    "Yalova": (40.6500, 29.2667),
    "Karabük": (41.2061, 32.6204),
    "Kilis": (36.7184, 37.1212),
    "Osmaniye": (37.0742, 36.2478),
    "Düzce": (40.8438, 31.1565)
}


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
            mekanlar = []

            lat, lon = sehir_koordinatlari[sehir]

            overpass_sorgu = f"""
            [out:json][timeout:25];

            nwr["amenity"~"^(bar|pub|nightclub)$"](around:10000,{lat},{lon});

            out center tags;
            """

             overpass_sunuculari = [
                "https://overpass-api.de/api/interpreter",
                "https://overpass.kumi.systems/api/interpreter",
                "https://overpass.nchc.org.tw/api/interpreter"
            ]

            overpass_veri = None

            for sunucu in overpass_sunuculari:
                try:
                    overpass_response = requests.get(
                        sunucu,
                        params={"data": overpass_sorgu},
                        headers={
                            "User-Agent": "KokteylMekanBulucu/1.0",
                            "Accept": "application/json"
                        },
                        timeout=20
                    )

                    overpass_response.raise_for_status()
                    overpass_veri = overpass_response.json()
                    break

                except requests.RequestException:
                    continue

            if overpass_veri is None:
                st.warning(
                    "⚠️ Mekan sunucuları şu an yoğun. Biraz sonra tekrar deneyebilirsin."
                )
                overpass_veri = {"elements": []}

            for yer in overpass_veri.get("elements", []):

                tags = yer.get("tags", {})
                isim = tags.get("name")

                if not isim:
                    continue

                yer_lat = yer.get("lat")
                yer_lon = yer.get("lon")

                if yer_lat is None or yer_lon is None:
                    center = yer.get("center", {})
                    yer_lat = center.get("lat")
                    yer_lon = center.get("lon")

                if yer_lat is None or yer_lon is None:
                    continue

                tur = tags.get("amenity", "mekan")
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

            uygun_mekanlar = [
                m for m in mekanlar
                if m["puan"] > 0
            ]

            mekanlar = sorted(
                uygun_mekanlar,
                key=lambda x: x["puan"],
                reverse=True
            )[:10]

            if mekanlar:

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
