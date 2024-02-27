from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import requests
import os

url = "https://nalburtek.com/el-aletleri/demirci-el-aletleri"
ana_kat = url.replace("https://nalburtek.com/", "").replace("/", " ").replace("-", " ")

# Selenium WebDriver'ı başlat
driver = webdriver.Chrome()  # Chrome tarayıcı kullanılacaksa ChromeDriver'ın yüklü olması gerekmektedir
driver.get(url)

# Sayfaları dolaşmak için döngü
liste = []
try:
    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        st1 = soup.find("div", attrs={"class": "col-12 listRightBlock pb-4 pt-3"})
        st2 = st1.find("div", attrs={"class": "row urunList m-0"})
        st3 = st2.find_all("div", attrs={"class": "col-xl-2 col-lg-2 col-md-4 col-sm-4 col-6 p-0 productItem"})

        for detaylar in st3:
            link_sonu = detaylar.find("meta", attrs={"itemprop": "url"}).get("content")
            link_basi = "https://nalburtek.com"
            link = link_basi + link_sonu
            r1 = requests.get(link)
            soup1 = BeautifulSoup(r1.content, "html.parser")

            stok_no_element = soup1.find("div", attrs={"itemprop": "sku"})
            stok_no = stok_no_element.text.strip() if stok_no_element else ""

            fiyat_element = soup1.find("span", attrs={"class": "price-sticker"})
            fiyat = fiyat_element.text.strip() if fiyat_element else ""

            urun_adi_element = soup1.find("strong", attrs={"itemprop": "name"})
            urun_adi = urun_adi_element.text.strip() if urun_adi_element else ""

            marka_element = soup1.find("a", attrs={"itemprop": "brand"})
            marka = marka_element.text.strip() if marka_element else ""

            urun_foto_element = soup1.find("a", class_="detailImageGroup")
            urun_foto = urun_foto_element.find("img").get("src") if urun_foto_element else ""

            if urun_foto:
            # Resmi indirerek kaydet
                response = requests.get(urun_foto)

                if response.status_code == 200:
            # Resim dosyasını ana_kat ismi ile kaydet
                    resim_adi1 = f"{stok_no}.jpg"
                    resim_adi2=resim_adi1.replace(":","") # Örneğin, stok numarasını kullanarak bir isim oluşturabilirsiniz
                    resim_yolu = os.path.join("", resim_adi2)  # resimler klasörü altında kaydedin (klasörü oluşturmanız gerekebilir)
                    with open(resim_yolu, "wb") as f:
                        f.write(response.content)
                    urun_foto = resim_yolu  # Resim dosyasının yerel yolunu liste verisine ekleyin
                else:
                    urun_foto = ""  # Resim indirilemezse boş bırakın
            else:
                    urun_foto = ""  # Resim yoksa boş bırakın

            liste.append([stok_no, urun_adi, marka, fiyat, urun_foto])

        # "Sonraki" düğmesine tıklama
        #next_button = WebDriverWait(driver, 10).until(
        #   EC.presence_of_element_located((By.CLASS_NAME, "paginationjs-next"))
        #)
        #if "disabled" in next_button.get_attribute("class"):
        #    break  # Son sayfaya gelindi, döngüyü sonlandır
        #else:
        #    driver.execute_script("arguments[0].click();", next_button)

finally:
    driver.quit()  # WebDriver'ı kapat

    df = pd.DataFrame(liste)
    df.columns = ["ID", "AD", "MARKA", "FIYAT", "FOTO"]
    df.to_excel(ana_kat + ".xlsx")
