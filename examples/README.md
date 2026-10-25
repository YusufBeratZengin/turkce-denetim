# Örnek Dosyalar ve Kullanım Senaryoları

Bu dizin, `turkce-denetim` aracının farklı kullanım senaryolarını gösteren örnek dosyaları içerir:

| Dosya | Açıklama |
|---|---|
| `bad.md` | Yapay zekâ basmakalıpları, çeviri kokusu ve imla hataları içeren sorunlu metin örneği. |
| `bad.expected.txt` | `bad.md` dosyasının terminal denetiminden beklenen altın (golden) çıktısı. |
| `good.md` | Temiz, yalın ve akıcı Türkçe ile kaleme alınmış hatasız metin örneği. |
| `api_usage.py` | `turkce-denetim` kütüphanesini doğrudan Python kodunda çağırma ve sonuçları işleme betiği. |
| `custom_config.toml` | Kural eşiklerini ayarlama ve kural kapatma seçeneklerini gösteren örnek yapılandırma dosyası. |
| `pre-commit-config.yaml` | Git depolarına eklemek için hazır pre-commit kanca yapılandırması. |

## Hızlı Denemeler

Komut satırından bu örnekleri sınayabilirsiniz:

```bash
# Sorunlu metni denetleyin
turkce-denetim examples/bad.md --no-color

# Temiz metni denetleyin
turkce-denetim examples/good.md --no-color

# Özel yapılandırma dosyasıyla çalıştırın
turkce-denetim examples/bad.md --config examples/custom_config.toml

# Python API kullanım örneğini çalıştırın
python examples/api_usage.py
```
