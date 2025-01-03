# Blog Uygulaması

Bu proje, bir blog platformu oluşturmak için geliştirilmiş bir web uygulamasıdır. Kullanıcılar makaleler oluşturabilir, görüntüleyebilir ve arama yapabilirler. Uygulama, Flask framework'u ile geliştirilmiştir ve MySQL veritabanı kullanılarak veri yönetimi yapılmaktadır.

## Özellikler
- Kullanıcı kaydı ve giriş işlemleri
- Makale oluşturma, düzenleme ve silme
- Makale arama ve listeleme
- Kullanıcı panosu (admin paneli)

## Teknolojiler
- Python
- Flask
- MySQL
- HTML, CSS, JavaScript

## Proje Kurulumu

1. **Gerekli Bağımlılıkları Yükleyin**:
   Projenin bağımlılıklarını yüklemek için şu komutu çalıştırın:
pip install -r requirements.txt

2. **Veritabanını Yapılandırın**:
Proje, MySQL veritabanı kullanmaktadır. Veritabanını doğru bir şekilde yapılandırmak için aşağıdaki adımları takip edin:
- `config.py` dosyasındaki MySQL bağlantı bilgilerini doldurun.
- Veritabanı şemalarını oluşturmak için gerekli SQL dosyasını çalıştırın.

3. **Uygulamayı Başlatın**:
Flask uygulamasını başlatmak için şu komutu kullanabilirsiniz:
python blog.py

Uygulama, local ağda çalışacak şekilde yapılandırılmıştır ve domain kullanılmamıştır.

## Kullanıcı Girişi

- **Kayıt Olma**: Kullanıcılar yeni bir hesap oluşturabilirler.
- **Giriş Yapma**: Kayıtlı kullanıcılar sisteme giriş yapabilirler.

## Notlar

- Proje tamamen yerel bilgisayar ağında çalışacak şekilde yapılandırılmıştır. Bir domain veya online barındırma kullanılmamaktadır.
