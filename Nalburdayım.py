from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd

url = "https://www.nalburdayim.com/hela-taslari"
ana_kat = url.replace("https://www.nalburdayim.com/", "").replace("/", " ").replace("-", " ").replace("?", " ").replace("=", " ")
Döviz = "TL"
KDV = 20

# Selenium WebDriver'ı başlat
driver = webdriver.Chrome()
driver.get(url)

# Ürünleri depolamak için boş bir liste ve daha önce eklenen ürünleri kontrol etmek için küme oluşturun
liste = []
urunler = set()

# Döngüyü başlatmadan önce link_sonraki'yi tanımlayalım
link_sonraki = ""

while True:
    soup = BeautifulSoup(driver.page_source, "html.parser")
    st1 = soup.find("div", attrs={"id": "ProductListMainContainer"})
    st2 = st1.find("div", attrs={"class": "ProductList sort_4"})
    st3 = st2.find_all("div", attrs={"class": "ItemOrj col-lg-3 col-md-3 col-sm-4 col-xs-6"})

    if len(st3) == 0:
        break  # Eğer sayfada ürün yoksa döngüyü sonlandır

    for detaylar in st3:

        link_sonu = detaylar.find("a", attrs={"class": "detailLink detailUrl"}).get("href")
        link_basi = "https://www.nalburdayim.com/"
        link = link_basi + link_sonu
        driver.get(link)
        soup1 = BeautifulSoup(driver.page_source, "html.parser")

        urun_adi_element = soup1.find("div", attrs={"class": "ProductName"})
        if urun_adi_element:
            urun_adi = urun_adi_element.find("span").text.strip()
        else:
            print("Ürün adı bulunamadı.")
            continue  # Bu ürünü atlayarak döngüye devam et

        Marka_element = soup1.find("span", attrs={"class": "right_line Marka"})
        Marka = Marka_element.text.strip() if Marka_element else ""

        fiyat_element = soup1.find("span", class_="spanFiyat")
        fiyat = fiyat_element.text.strip() if fiyat_element else ""
        fiyat = fiyat.replace("₺", "").strip()

        urun_foto_element = soup1.find("img", class_="cloudzoom-gallery lazyImage entered loaded")
        if urun_foto_element and "src" in urun_foto_element.attrs:
            urun_foto = urun_foto_element["src"]
        else:
           urun_foto = "boş"
           print(urun_foto)

        # Eğer aynı ürün daha önce eklenmişse, döngüyü sonlandır
        if urun_adi in urunler:
            break

        urunler.add(urun_adi)  # Ürünü görülenler listesine ekle

        liste.append([ana_kat, urun_adi, Marka, fiyat, Döviz, KDV, urun_foto])

    # Sonraki sayfaya geçiş işlemi
    try:
        sayfa_sonraki = soup.find("a", class_="butonDisabled SelectedSayfa").find_next_sibling("a")
        if not sayfa_sonraki:
            break  # Sonraki sayfa bağlantısı yoksa döngüyü sonlandır
        link_sonraki = url + sayfa_sonraki["href"]
    except AttributeError:
        break  # Sonraki sayfa bağlantısı yoksa döngüyü sonlandır
    driver.get(link_sonraki)

driver.quit()  # WebDriver'ı kapat

df = pd.DataFrame(liste)
df.columns = ["Kategori", "Ürün", "Marka", "Fiyat", "Döviz", "KDV", "URL"]
df.to_excel("Nalburdayım.xlsx", index=True, header=True, engine='openpyxl')
