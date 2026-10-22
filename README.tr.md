# turkce-denetim

Türkçe metinlerde yapay zekâ kokusu, çeviri kalıpları ve biçimsel yazım sorunlarını tespit eden, kural tabanlı (LLM'siz, sıfır çalışma bağımlılığı) linter ve komut satırı aracı.

[English Documentation (README.md)](README.md)

---

## Önemli Uyarı

> **Bu araç bir metnin yapay zekâ tarafından yazıldığını kesin olarak kanıtlamaz.**
> Yalnızca yapay zekâ modellerinin ürettiği metinlerde ve İngilizceden yapılan mekanik çevirilerde sıkça tekrarlanan basmakalıp üslup kalıplarını, çeviri kokularını ve yazım sorunlarını nesnel kurallarla gösterir. Doğal olarak yazılmış bir metin nadiren de olsa bu kuralları tetikleyebilir veya yapay zekâ metinleri bu kalıplardan arındırılarak yazılmış olabilir. Doğallık puanı bağlayıcı bir hüküm değil, yazara yardımcı bir editoryal göstergedir.

---

## Öne Çıkan Özellikler

- **Çalışma Bağımlılığı Yok**: Yalnızca Python standart kütüphanesini kullanır (Python >= 3.10). Harici NLP veya makine öğrenmesi paketine ihtiyaç duymaz.
- **25 Özelleşmiş Kural**: Çeviri kalıpları, yapay zekâ basmakalıpları, okunabilirlik ve yüksek güvenli yazım kuralları.
- **Doğru Türkçe Harf Dönüşümü**: `İ/i` ve `I/ı` harflerinin büyük/küçük harf ve casefold dönüşümleri tam tutarlılıkla işletilir.
- **Türkçe Ek Budayıcı (Stemmer)**: Sondan eklemeli Türkçe yapısına uygun, harici paket gerektirmeyen kural tabanlı ek budayıcı ile yakın kelime kökü tekrarlarını tespit eder.
- **Markdown Uyumlu**: Fenced kod bloklarını (```` ``` ```` ve `~~~`) ve satır içi kodları (`` `...` ``) boşlukla maskeleyerek satır ve sütun konumlarını bozmadan kod dışı metinleri denetler.
- **Farklı Çıktı Biçimleri**: Renkli terminal metni, makine okur JSON (`--format json`) ve GitHub Code Scanning ile tam uyumlu SARIF 2.1.0 (`--format sarif`).
- **Doğallık Puanı (0-100)**: 100 kelime başına düşen ağırlıklı bulgu yoğunluğunu hesaplayan şeffaf matematiksel puanlama.
- **Yapılandırılabilir**: `pyproject.toml` (`[tool.turkce-denetim]`) üzerinden veya komut satırı bayraklarıyla (`--disable`, `--min-severity`) kurallar yönetilebilir.

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
# Mevcut dizindeki tüm .md ve .txt dosyalarını denetle
turkce-denetim

# Belirli bir dosya ya da dizini tara
turkce-denetim metin.md
turkce-denetim docs/

# Standart girdiden (stdin) metin oku
cat taslak.txt | turkce-denetim -

# JSON çıktısı al
turkce-denetim metin.md --format json

# GitHub Code Scanning için SARIF raporu oluştur
turkce-denetim docs/ --format sarif > sonuclar.sarif

# Belirli kuralları kapat
turkce-denetim metin.md --disable TD001,TD005

# Yalnızca belirli önem derecesindeki bulguları listele (info, warn, error)
turkce-denetim metin.md --min-severity warn

# Yalnızca doğallık puanını sayı olarak yazdır
turkce-denetim metin.md --score-only
```

### CLI Seçenekleri

| Seçenek | Tür | Varsayılan | Açıklama |
|---|---|---|---|
| `targets` | Konumsal | `.` | Denetlenecek dosya, dizin veya standart girdi için `-`. |
| `-f, --format` | Seçenek | `text` | Çıktı biçimi: `text`, `json`, `sarif`. |
| `-d, --disable` | Metin | Yok | Devre dışı bırakılacak kural kimlikleri (örn: `TD001,TD003`). |
| `-s, --min-severity`| Seçenek | `info` | Asgari önem eşiği: `info`, `warn`, `error`. |
| `-c, --config` | Yol | Yok | Özel TOML yapılandırma dosyası yolu. |
| `--no-color` | Bayrak | False | Terminal çıktısındaki ANSI renklerini kapatır. |
| `--score-only` | Bayrak | False | Yalnızca hesaplanan sayısal doğallık puanını basar. |
| `-v, --version` | Bayrak | | Sürüm bilgisini görüntüler. |

---

## Kural Kataloğu

Linter 4 ana kategoride 25 kural uygular:

### 1. Çeviri Kalıpları (Translation Patterns)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD001` | `ile-birlikte-asiri` | `warn` | "Gelişmeler ile birlikte yeni imkânlar doğdu." | "ile", "-le/-la" veya doğrudan bağlaç tercih edin. |
| `TD002` | `bu-noktada` | `warn` | "Bu noktada dikkat edilmesi gerekir." | "burada", "bu aşamada" veya doğrudan konuya giren bir ifade kullanın. |
| `TD003` | `gunun-sonunda` | `warn` | "Günün sonunda karar verildi." | "at the end of the day" çevirisi yerine "sonuçta", "özünde" veya "nihayetinde" kullanın. |
| `TD004` | `onemlidir-ki` | `warn` | "Şunu belirtmek önemlidir ki bu bir hatadır." | "it is important that" çevirisi yerine "...belirtmek gerekir" veya "...önem taşır" tercih edin. |
| `TD005` | `konusunda-yigilmasi` | `warn` | "Veri güvenliği konusunda ve mimari konusundaki..." | Aynı cümlede "konusunda" kümelenmesi yerine "-e dair", "-le ilgili" veya doğrudan yönelme hali kullanın. |
| `TD006` | `sahip-olmak` | `warn` | "Bu model yüksek bir hıza sahiptir." | "have" çevirisi yerine iyelik eki ("hızı yüksektir") veya "vardır / bulunur" tercih edin. |
| `TD007` | `edilgen-yigilmasi` | `warn` | "Planlar yapıldı, bütçe onaylandı ve görevler dağıtıldı." | Aynı cümlede 3+ edilgen fiil yerine etken çatı kullanarak özneyi belirginleştirin. |

### 2. Yapay Zekâ Kalıpları (AI Patterns)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD008` | `elbette-acilis` | `warn` | "Elbette! Size bu konuda yardımcı olayım." | Dalkavukça açılışı silerek doğrudan bilgiye veya yanıta geçin. |
| `TD009` | `harika-soru` | `warn` | "Harika bir soru sordunuz." | Basmakalıp övgü cümlesini silerek doğrudan yanıt verin. |
| `TD010` | `sonuc-olarak-kapanis` | `info` | "Sonuç olarak, bu yöntemlerin tümü etkilidir." | Kapanış paragrafını basmakalıp özet bağlacı yerine doğrudan ana fikirle açın. |
| `TD011` | `dunyasi-metaforu` | `info` | "Yapay zekâ dünyasında her gün yeni bir adım..." | "...dünyasında" yerine doğrudan alan adını kullanın ("yapay zekâda", "yazılımda"). |
| `TD012` | `yolculuk-metaforu` | `warn` | "Dijital dönüşüm yolculuğumuz başladı." | Soyut süreçler için basmakalıp "yolculuk" yerine "süreci", "adımları" veya somut aşamaları yazın. |
| `TD013` | `derinlemesine` | `info` | "Bu konuyu derinlemesine inceleyelim." | Abartı zarfı yerine "ayrıntılı biçimde" veya doğrudan "inceleyelim" eylemini kullanın. |
| `TD014` | `kapsamli-sekilde` | `info` | "Raporu kapsamlı bir şekilde hazırladık." | Dolgu yapısı yerine "kapsamlıca" veya doğrudan fiili kullanın. |
| `TD015` | `uclu-sifat-dizisi` | `info` | "Hızlı, güvenli ve esnek bir yapı kurmalıyız." | Üçlü sıfat tamlamasını sadeleştirin; iddiaları somut kanıtlarla veya bağımsız cümlelerle açın. |
| `TD016` | `paragraf-acilis-tekrari` | `warn` | Ardışık iki paragrafın da "Ayrıca..." ile başlaması. | Paragraf girişlerini çeşitlendirin. |

### 3. Okunabilirlik ve Akış (Readability)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD017` | `cumle-uzunlugu` | `warn` | 35 kelimeyi aşan cümle. | Cümleyi iki veya daha fazla bağımsız cümleye bölün. |
| `TD018` | `paragraf-uzunlugu` | `info` | 120 kelimeyi aşan blok paragraf. | Paragrafı alt düşünce bloklarına veya alt başlıklara bölün. |
| `TD019` | `yakin-kelime-tekrari` | `warn` | Aynı kökün (örn: "yaz-") aynı cümlede 3+ kez geçmesi. | Tekrarlayan kelimeler yerine zamir veya eşanlamlı sözcük kullanın. |
| `TD020` | `virgul-zinciri` | `info` | Tek bir cümlede 5 veya daha fazla virgül bulunması. | Cümleyi bölün veya noktalı virgül ya da liste biçimi kullanın. |
| `TD025` | `veya-baglac-tekrari` | `info` | Tek bir cümlede 3 veya daha fazla "ve / veya" geçmesi. | Bağlaç yığılması yerine virgüllü sıralama yapın veya cümleyi bölün. |

### 4. Yazım ve Tipografi (Spelling & Typography)

| Kimlik | Kural Adı | Önem | Hatalı / Sorunlu Örnek | Düzeltme Önerisi |
|---|---|---|---|---|
| `TD021` | `de-da-baglaci` | `error` | "Gittide söylemedi" / "Ev de kaldım" | Bağlaç olan "de/da" ayrı yazılır; bulunma durumu eki bitişik yazılır. |
| `TD022` | `ki-baglaci` | `error` | "Gördümki her şey yolunda" / "Demekki" | Fiilden sonra gelen "ki" bağlaçtır ve ayrı yazılır. |
| `TD023` | `bilesik-ayri-yazim` | `error` | "herşey", "hiçbirşey", "bir çok", "farketmek" | TDK imla kurallarına uygun biçimi kullanın ("her şey", "birçok", "fark etmek"). |
| `TD024` | `tirnak-tutarsizligi` | `info` | Aynı metinde hem düz `"` hem kıvrık `“”` tırnak karışımı. | Belge genelinde tek ve tutarlı bir tırnak/kesme stili seçin. |

---

## Doğallık Puanı Formülü

Doğallık Puanı, 100 kelime başına düşen bulgu yoğunluğunu ölçen $0.0 - 100.0$ arası bir metriktir.

1. Her bulgu önem derecesine göre ceza katsayısı alır:
   - **Error (Hata)**: $8.0$ puan
   - **Warning (Uyarı)**: $3.0$ puan
   - **Info (Bilgi)**: $1.0$ puan
2. Toplam ceza, metnin kelime sayısına ($W$) göre 100 kelimeye oranlanır (küçük metinlerde aşırı cezalandırmayı önlemek için en az 50 kelime taban alınır):
   $$\text{Normallestirilmis Ceza} = \frac{\sum \text{Cezalar} \times 100}{\max(W, 50)}$$
3. Nihai puan sınırlandırılır ve bir ondalık basamakla yuvarlanır:
   $$\text{Doğallık Puanı} = \max(0.0, \min(100.0, 100.0 - \text{Normallestirilmis Ceza}))$$

### Puan Aralıkları

| Puan Aralığı | Derece | Açıklama |
|---|---|---|
| **90.0 – 100.0** | Yüksek Doğallık | Temiz, akıcı ve yapay kalıplardan arınmış doğal Türkçe. |
| **75.0 – 89.9** | İyi | Okunaklı, yalnızca birkaç münferit kalıp veya dolgu içeren metin. |
| **50.0 – 74.9** | Orta | Belirgin yapay zekâ veya çeviri kokusu barındıran metin. Düzeltme önerilir. |
| **0.0 – 49.9** | Düşük | Yoğun sentetik kalıplar, çeviri basmakalıpları veya yazım hataları. |

---

## Yapılandırma (`pyproject.toml`)

Projenizin `pyproject.toml` dosyasına denetim kurallarını ekleyebilirsiniz:

```toml
[tool.turkce-denetim]
# Raporlanacak asgari onem derecesi ("info", "warn", "error")
min_severity = "info"

# Devre disi birakilacak kurallar
disable = ["TD001", "TD014"]

# Esik degerleri
max_sentence_words = 35
max_paragraph_words = 120
max_commas_per_sentence = 5
min_word_repetition = 3
```

---

## GitHub Actions Entegrasyonu

Pull request'lerde otomatik denetim yapıp bulguları GitHub Code Scanning sekmesinde incelemek için:

```yaml
name: Turkce Metin Denetimi

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

      - name: turkce-denetim yukle
        run: pip install turkce-denetim

      - name: Metinleri denetle ve SARIF uret
        run: turkce-denetim . --format sarif > sonuclar.sarif
        continue-on-error: true

      - name: SARIF raporunu yukle
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: sonuclar.sarif
```

---

## Python Kütüphanesi Olarak Kullanım

```python
from turkce_denetim import Config, analyze_text

metin = "Bu noktada konuyu derinlemesine incelemek çok önemlidir ki sonuç alalım."
config = Config(min_severity="warn")

sonuc = analyze_text(metin, config)

print(f"Kelime Sayısı : {sonuc.word_count}")
print(f"Doğallık Puanı: {sonuc.naturalness_score} / 100")

for bulgu in sonuc.findings:
    print(f"Satır {bulgu.line}:{bulgu.column} [{bulgu.rule_id}] {bulgu.message}")
    if bulgu.suggestion:
        print(f"  Öneri: {bulgu.suggestion}")
```

---

## Lisans

Bu proje [MIT Lisansı](LICENSE) kapsamında lisanslanmıştır.

Copyright (c) 2026 Yusuf Berat Zengin
