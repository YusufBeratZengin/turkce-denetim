# turkce-denetim

Türkçe metinlerdeki yapay zekâ kokusunu, çeviri kalıplarını ve yazım sorunlarını bulan bir yazı denetleyici (linter) ve komut satırı aracı. Kurallara dayanır, dil modeli kullanmaz, kurulumda ek paket istemez.

[English Documentation (README.md)](README.md)

---

## Önemli Uyarı

> **Bu araç bir metnin yapay zekâ tarafından yazıldığını kesin olarak kanıtlamaz.**
> Yalnızca yapay zekâ metinlerinde ve İngilizceden birebir çevrilmiş yazılarda sık görülen basmakalıpları, çeviri kokusunu ve yazım hatalarını gösterir. İnsanın yazdığı bir metin de arada bu kurallara takılabilir; yapay zekâ metni de bu kalıplardan temizlenmiş olabilir. Doğallık puanı kesin bir hüküm vermez, yazarın işini kolaylaştıran bir göstergedir.

---

## Öne Çıkan Özellikler

- **Bağımlılık yok**: Yalnızca Python standart kütüphanesini kullanır (Python 3.10 ve üstü).
- **25 kural**: Çeviri kalıpları, yapay zekâ basmakalıpları, okunabilirlik ve yazım.
- **Doğru büyük/küçük harf**: `İ/i` ve `I/ı` ayrımını Türkçe kurallarına göre yapar.
- **Ek budayıcı (stemmer)**: Aynı kökten gelen sözcüklerin bir cümlede fazla tekrarlanmasını, dış paket kullanmadan yakalar.
- **Markdown bilir**: Kod bloklarını (```` ``` ```` ve `~~~`) ve satır içi kodu (`` `...` ``) boşlukla maskeler; satır ve sütun numaraları bozulmaz.
- **Üç çıktı biçimi**: Renkli terminal çıktısı, JSON (`--format json`) ve GitHub Code Scanning için SARIF 2.1.0 (`--format sarif`).
- **Doğallık puanı (0-100)**: Bulguların yüz sözcüğe düşen ağırlığından hesaplanır; formül aşağıda açık yazılı.
- **Ayarlanabilir**: `pyproject.toml` içindeki `[tool.turkce-denetim]` bölümünden ya da `--disable` ve `--min-severity` bayraklarından.

---

## Kurulum

Pip ile yükleme:

```bash
pip install turkce-denetim
```

Geliştirici ortamı kurulumu:

```bash
git clone https://github.com/YusufBeratZengin/turkce-denetim.git
cd turkce-denetim
python -m venv .venv
source .venv/bin/activate  # Windows için: .\.venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Kullanım

### Komut Satırı Arayüzü (CLI)

```bash
# Bulunduğun dizindeki tüm .md ve .txt dosyalarını denetle
turkce-denetim

# Komut PATH'te değilse aynısı modül olarak da çalışır
python -m turkce_denetim metin.md

# Belirli bir dosya ya da dizini tara
turkce-denetim metin.md
turkce-denetim docs/

# Metni standart girdiden (stdin) oku
cat taslak.txt | turkce-denetim -

# JSON çıktısı
turkce-denetim metin.md --format json

# GitHub Code Scanning için SARIF raporu
turkce-denetim docs/ --format sarif > sonuclar.sarif

# Bazı kuralları kapat
turkce-denetim metin.md --disable TD001,TD005

# Yalnızca warn ve error düzeyindeki bulguları göster
turkce-denetim metin.md --min-severity warn

# Sadece doğallık puanını yazdır
turkce-denetim metin.md --score-only

# Mevcut tüm kuralları listele
turkce-denetim --list-rules
```

### CLI Seçenekleri

| Seçenek | Tür | Varsayılan | Açıklama |
|---|---|---|---|
| `targets` | Konumsal | `.` | Denetlenecek dosya ya da dizin; stdin için `-`. |
| `-f, --format` | Seçenek | `text` | Çıktı biçimi: `text`, `json`, `sarif`. |
| `-d, --disable` | Metin | Yok | Kapatılacak kural kimlikleri, virgülle ayrılır (örn: `TD001,TD003`). |
| `-s, --min-severity`| Seçenek | `info` | Gösterilecek en düşük önem: `info`, `warn`, `error`. |
| `-c, --config` | Yol | Yok | Kendi TOML yapılandırma dosyanın yolu. |
| `--no-color` | Bayrak | False | Terminal renklerini kapatır. |
| `--score-only` | Bayrak | False | Yalnızca doğallık puanını yazar. |
| `--list-rules` | Bayrak | False | Mevcut tüm kuralları listeler (kimlik, ad, önem ve açıklama). |
| `-v, --version` | Bayrak | | Sürümü yazar. |

### Çıkış Kodları (Exit Codes)

| Kod | Anlamı |
|---|---|
| `0` | Başarılı: hata (`error`) düzeyinde bulgu tespit edilmedi (metin temiz veya yalnızca `info`/`warn` önerileri içeriyor). |
| `1` | Denetim hatası: bir veya daha fazla `error` önem derecesinde bulgu tespit edildi (örn. yazım ve bağlaç hataları). |
| `2` | Kullanım, yapılandırma veya G/Ç (I/O) hatası: geçersiz CLI bağımsız değişkenleri, okunamayan dosyalar veya hatalı TOML yapılandırması. |

### Canlı Örnek (Live Demo)

```bash
$ turkce-denetim examples/bad.md --no-color
examples/bad.md:1:1: warn  [TD008] Metin başında dalkavukça yapay zekâ açılışı tespit edildi ('Elbette!').
    öneri: Dalkavukça açılış yerine doğrudan konuya veya bilgiye girin.
examples/bad.md:1:74: info  [TD001] 'gelişmesi ile birlikte' kalıbı çeviri kokusu taşıyabilir; daha yalın bağlaçlar tercih edilebilir.
    öneri: 'ile birlikte' yerine 'ile', 'bunun yanında', 'ayrıca' veya yalın ek kullanın.
examples/bad.md:3:1: info  [TD002] Cümle başında 'Bu noktada' dolgu ifadesi tespit edildi.
    öneri: 'Bu noktada' yerine 'burada', 'bu aşamada' veya doğrudan konuya giren bir ifade tercih edin.
examples/bad.md:3:12: warn  [TD012] 'dijital dönüşüm yolculuğumuz' klişesi yapay zekâ metinlerinde soyut 'journey' çevirisidir.
    öneri: 'Yolculuk' metaforu yerine 'süreci', 'adımları' veya somut aşamaları yazın.
examples/bad.md:3:75: info  [TD013] 'derinlemesine incelemek' ifadesi yapay zekânın sık kullandığı abartılı bir dolgudur.
    öneri: 'Derinlemesine' yerine 'ayrıntılı biçimde', 'kapsamlıca' veya doğrudan eylemin kendisini yazın.
examples/bad.md:3:103: warn  [TD004] 'önemlidir ki' kalıbı İngilizce 'it is important that' çevirisidir.
    öneri: '...önemlidir ki' yerine '...belirtmek gerekir', '...önem taşır' veya doğrudan yargı cümlesi kurun.
examples/bad.md:5:14: error [TD023] 'herşey' yazımı hatalı; doğrusu 'her şey' olmalıdır.
    öneri: her şey

--- Denetim Özeti ---
Taranan belge sayısı : 1
Toplam kelime sayısı : 39
Bulgular             : 1 hata, 3 uyarı, 3 bilgi (toplam 7)
Kural dağılımı       : TD001: 1, TD002: 1, TD004: 1, TD008: 1, TD012: 1, TD013: 1, TD023: 1
Doğallık Puanı       : 60.0 / 100 (Orta (Belirgin yapay zekâ veya çeviri kokusu))
```

---

## Kural Kataloğu

25 kural dört grupta toplanır. `error` düzeyinde bulgu varsa çıkış kodu 1, yoksa 0'dır.

### 1. Çeviri Kalıpları (Translation Patterns)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD001` | `ile-birlikte-asiri` | `info` | "Gelişmeler ile birlikte yeni imkânlar doğdu." | "Gelişmelerle birlikte" ya da "Gelişmeler sayesinde" gibi yalın bir yapı seçin. "Bununla birlikte" ve "arkadaşımla birlikte" gibi doğal kullanımlara dokunmaz. |
| `TD002` | `bu-noktada` | `info` | "Bu noktada dikkat edilmesi gerekir." | Cümleyi "Burada" ya da "Bu aşamada" ile açın veya doğrudan konuya girin. Yalnızca cümle başındaki kullanımı yakalar. |
| `TD003` | `gunun-sonunda` | `warn` | "Günün sonunda, karar verildi." | "At the end of the day" çevirisi yerine "sonuçta", "özünde" ya da "nihayetinde" yazın. "Günün sonunda eve döndük" gibi gerçek zaman anlatımına dokunmaz. |
| `TD004` | `onemlidir-ki` | `warn` | "Şunu belirtmek önemlidir ki bu bir hatadır." | "It is important that" çevirisi yerine "...belirtmek gerekir" ya da "...önem taşır" deyin. |
| `TD005` | `konusunda-yigilmasi` | `warn` | "Veri güvenliği konusunda ve mimari konusundaki..." | Aynı cümlede "konusunda" üst üste gelmesin; "-e dair", "-le ilgili" ya da yönelme eki kullanın. |
| `TD006` | `sahip-olmak` | `warn` | "Bu model yüksek bir hıza sahiptir." | "Have" çevirisi yerine iyelik eki ("hızı yüksektir") ya da "vardır" kullanın. "Sahip olmak istiyorum" ve "sahip çıkmak" gibi doğal kullanımlara dokunmaz. |
| `TD007` | `edilgen-yigilmasi` | `warn` | "Planlar yapıldı, bütçe onaylandı ve görevler dağıtıldı." | Aynı cümlede üç ya da daha fazla edilgen fiil varsa etken çatıya geçip özneyi görünür kılın. |

### 2. Yapay Zekâ Kalıpları (AI Patterns)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD008` | `elbette-acilis` | `warn` | "Elbette! Size bu konuda yardımcı olayım." | Dalkavukça açılışı silin, doğrudan cevaba geçin. |
| `TD009` | `harika-soru` | `warn` | "Harika bir soru sordunuz." | Övgü cümlesini silin, doğrudan cevap verin. |
| `TD010` | `sonuc-olarak-kapanis` | `info` | "Sonuç olarak, bu yöntemlerin tümü etkilidir." | Kapanış paragrafını "Sonuç olarak" demeden, ana fikirle açın. |
| `TD011` | `dunyasi-metaforu` | `info` | "Yapay zekâ dünyasında her gün yeni bir adım..." | "...dünyasında" yerine alanın adını söyleyin ("yapay zekâda", "yazılımda"). Yalnızca yazılım, teknoloji, dijital gibi klişeleşmiş alan adlarını yakalar; "çocukların dünyasında" gibi kullanımlara dokunmaz. |
| `TD012` | `yolculuk-metaforu` | `warn` | "Dijital dönüşüm yolculuğumuz başladı." | Soyut işler için "yolculuk" yerine "süreç", "adımlar" ya da somut aşamaları yazın. Gerçek yolculuğa dokunmaz. |
| `TD013` | `derinlemesine` | `info` | "Bu konuyu derinlemesine inceleyelim." | "Derinlemesine" yerine "ayrıntılı" deyin ya da doğrudan "inceleyelim" yazın. |
| `TD014` | `kapsamli-sekilde` | `info` | "Raporu kapsamlı bir şekilde hazırladık." | "Kapsamlıca" ya da doğrudan fiil yeter. |
| `TD015` | `uclu-sifat-dizisi` | `info` | "Hızlı, güvenli ve esnek bir yapı kurmalıyız." | Sıfatları azaltın; iddiayı somut bir örnekle destekleyin. Yalnızca "çözüm, yaklaşım, sistem" gibi soyut bir adla biten üçlüleri yakalar. |
| `TD016` | `paragraf-acilis-tekrari` | `warn` | Ardışık iki paragrafın da "Ayrıca..." ile başlaması. | Paragraf girişlerini değiştirin. "Bu", "Şu" gibi zamirlerle başlayan paragraflar tekrar sayılmaz. |

### 3. Okunabilirlik ve Akış (Readability)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD017` | `cumle-uzunlugu` | `warn` | 35 sözcüğü aşan cümle. | Cümleyi ikiye bölün. |
| `TD018` | `paragraf-uzunlugu` | `info` | 120 sözcüğü aşan paragraf. | Paragrafı bölün ya da alt başlık ekleyin. |
| `TD019` | `yakin-kelime-tekrari` | `warn` | Aynı kökün (örn. "yaz-") bir cümlede üç kez geçmesi. | Zamir ya da eş anlamlı bir sözcük kullanın. |
| `TD020` | `virgul-zinciri` | `info` | Bir cümlede beş ya da daha fazla virgül. | Cümleyi bölün ya da madde işaretli liste yapın. |
| `TD025` | `veya-baglac-tekrari` | `info` | Bir cümlede üç ya da daha fazla "ve / veya". | Virgülle sıralayın ya da cümleyi bölün. |

### 4. Yazım ve Tipografi (Spelling & Typography)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD021` | `de-da-baglaci` | `error` | "Gittide söylemedi" / "Bende geldim" / "Ev de kaldım" | Bağlaç olan "de/da" ayrı, bulunma durumu eki bitişik yazılır. Yalnızca anlamı karıştırmayan kalıpları yakalar: "Bende bir sorun var", "grupta", "kulüpte" doğru yazımlardır. |
| `TD022` | `ki-baglaci` | `error` | "Gördümki her şey yolunda" / "Demekki" | Fiilden sonra gelen "ki" bağlaçtır, ayrı yazılır. |
| `TD023` | `bilesik-ayri-yazim` | `error` | "herşey", "hiçbirşey", "bir çok", "farketmek" | TDK yazımını kullanın ("her şey", "birçok", "fark etmek"). |
| `TD024` | `tirnak-tutarsizligi` | `info` | Aynı metinde hem düz `"` hem kıvrık `“”` tırnak karışımı. | Metin boyunca tek bir tırnak ve kesme stili kullanın. |

---

## Doğallık Puanı Formülü

Doğallık puanı 0 ile 100 arasında bir sayıdır ve bulguların yüz sözcüğe düşen yoğunluğunu ölçer.

1. Her bulgu önem derecesine göre ceza katsayısı alır:
   - **Error (Hata)**: $8.0$ puan
   - **Warning (Uyarı)**: $3.0$ puan
   - **Info (Bilgi)**: $1.0$ puan
2. Toplam ceza, sözcük sayısına ($W$) göre yüz sözcüğe oranlanır. Kısa metinler fazla cezalanmasın diye en az 50 sözcük esas alınır:
   $$\text{Normallestirilmis Ceza} = \frac{\sum \text{Cezalar} \times 100}{\max(W, 50)}$$
3. Puan 0 ile 100 arasına sıkıştırılır ve bir ondalık basamağa yuvarlanır:
   $$\text{Doğallık Puanı} = \max(0.0, \min(100.0, 100.0 - \text{Normallestirilmis Ceza}))$$

### Puan Aralıkları

| Puan Aralığı | Derece | Açıklama |
|---|---|---|
| **90.0 – 100.0** | Yüksek doğallık | Temiz, akıcı Türkçe. |
| **75.0 – 89.9** | İyi | Okunur; birkaç kalıp ya da dolgu var. |
| **50.0 – 74.9** | Orta | Yapay zekâ ya da çeviri kokusu belli oluyor; düzeltmek iyi olur. |
| **0.0 – 49.9** | Düşük | Çok sayıda basmakalıp, çeviri kokusu ya da yazım hatası. |

---

## Yapılandırma (`pyproject.toml`)

Ayarlar projenin `pyproject.toml` dosyasında tutulur:

```toml
[tool.turkce-denetim]
# Gösterilecek en düşük önem derecesi ("info", "warn", "error")
min_severity = "info"

# Kapatılacak kurallar
disable = ["TD001", "TD014"]

# Eşik değerleri
max_sentence_words = 35
max_paragraph_words = 120
max_commas_per_sentence = 5
min_word_repetition = 3
```

---

## GitHub Actions Entegrasyonu

Pull request'lerde metinleri otomatik denetleyip bulguları GitHub Code Scanning sekmesinde görmek için:

```yaml
name: Türkçe Metin Denetimi

on:
  pull_request:
    branches: [main]

jobs:
  lint-text:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: turkce-denetim kur
        run: pip install turkce-denetim

      - name: Metinleri denetle, SARIF üret
        run: turkce-denetim . --format sarif > sonuclar.sarif
        continue-on-error: true

      - name: SARIF raporunu yükle
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: sonuclar.sarif
```

---

## Pre-commit Entegrasyonu

Projenizin `.pre-commit-config.yaml` dosyasına ekleyerek her commit öncesinde Markdown ve metin dosyalarını otomatik denetleyebilirsiniz:

```yaml
repos:
  - repo: https://github.com/YusufBeratZengin/turkce-denetim
    rev: v0.1.0
    hooks:
      - id: turkce-denetim
```

---

## Python Kütüphanesi Olarak Kullanım

```python
from turkce_denetim import Config, analyze_text

metin = "Bu noktada konuyu derinlemesine incelemek çok önemlidir ki sonuç alalım."
config = Config(min_severity="warn")  # "info", "warn" ya da "error"

sonuc = analyze_text(metin, config)

print(f"Sözcük sayısı : {sonuc.word_count}")
print(f"Doğallık puanı: {sonuc.naturalness_score} / 100")

for bulgu in sonuc.findings:
    print(f"Satır {bulgu.line}:{bulgu.column} [{bulgu.rule_id}] {bulgu.message}")
    if bulgu.suggestion:
        print(f"  Öneri: {bulgu.suggestion}")
```

---

## Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır.

Copyright (c) 2026 Yusuf Berat Zengin
