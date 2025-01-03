from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

# Kullanıcı Girişi kontrol Decorator'ı: Bu decorator, belirli bir route'a erişmeden önce kullanıcının giriş yapıp yapmadığını kontrol eder.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:  # Eğer kullanıcı oturum açmışsa, route'a devam edilir
            return f(*args, **kwargs)
        else:  # Eğer kullanıcı giriş yapmamışsa, login sayfasına yönlendirilir
            flash("Bu sayfayı görüntülemek için giriş yapmalısınız...", "danger")
            return redirect(url_for("login"))
    return decorated_function

# Kullanıcı Kayıt Formu: Kullanıcı adı, e-posta, parola ve parola doğrulama gibi alanları içeren bir form
class RegisterForm(Form):
    name = StringField("İsim Soyisim", validators=[validators.length(min=4, max=25),])
    username = StringField("Kullanıcı Adı", validators=[validators.length(min=5, max=35),])
    email = StringField("Email Adresi", validators=[validators.Email(message="Lütfen Geçerli Bir Mail Adresi Girin...")])
    password = PasswordField("Parola", validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname="confirm", message="Parolanız uyuşmuyor")  # Parola doğrulaması
    ])
    confirm = PasswordField("Parolanızı Doğrulayın")

# Kullanıcı Giriş Formu: Kullanıcı adı ve parola alanları içeriyor
class LoginForm(Form):
    username = StringField("Kullanıcı Adı:")
    password = PasswordField("Parola:")

# Flask uygulaması başlatılıyor
app = Flask(__name__)
app.secret_key = "ybblog"  # Oturum yönetimi için gizli anahtar

# Veritabanı bağlantı bilgileri
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"  # Sorgu sonuçlarının sözlük formatında dönmesini sağlıyor

# MySQL bağlantısı oluşturuluyor
mysql = MySQL(app)

# Ana Sayfa
@app.route("/")
def index():
    return render_template("index.html")

# Hakkında Sayfası
@app.route("/about")
def about():
    return render_template("about.html")
# Makale sayfası
@app.route("/articles")
def articles():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall()

        return render_template("articles.html",articles = articles)
    else: 
        return render_template("articles.html")


# Kontrol Paneli - Sadece giriş yapmış kullanıcılar erişebilir
@app.route("/dashboard")
@login_required
def dashboard():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles = articles)
    else:
        return render_template("dashboard.html")

    return render_template("dashboard.html")

# Kayıt Olma Sayfası
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)  # Formu oluşturuyor
    if request.method == "POST" and form.validate():  # Form gönderildiğinde ve doğrulandıysa
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)  # Parolayı şifreliyoruz

        # Veritabanı işlemleri için cursor oluşturuluyor
        cursor = mysql.connection.cursor()

        # Kullanıcıyı veritabanına ekleyen SQL sorgusu
        sorgu = "Insert into users(name, email, username, password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu, (name, email, username, password))  # Sorguyu çalıştırıyoruz
        mysql.connection.commit()  # Değişiklikleri kaydediyoruz
        cursor.close()

        flash("Başarıyla kayıt oldunuz...", "success")  # Kayıt başarı mesajı

        return redirect(url_for("login"))  # Login sayfasına yönlendirilir
    else:
        return render_template("register.html", form=form)  # Kayıt formu render edilir

# Giriş Sayfası
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)  # Giriş formu oluşturuluyor
    if request.method == "POST":  # Eğer form gönderilmişse
        username = form.username.data
        password_entered = form.password.data

        # Veritabanı işlemleri için cursor oluşturuluyor
        cursor = mysql.connection.cursor()
        sorgu = "Select * From users Where username = %s"  # Kullanıcı adı ile sorgulama yapılıyor
        result = cursor.execute(sorgu, (username,))

        if result > 0:  # Kullanıcı bulunduysa
            data = cursor.fetchone()  # Kullanıcı verilerini alıyoruz
            real_password = data["password"]  # Veritabanındaki şifreyi alıyoruz
            if sha256_crypt.verify(password_entered, real_password):  # Parolayı doğruluyoruz
                flash("Başarıyla Giriş Yaptınız...", "success")

                session["logged_in"] = True  # Oturum açıldığını kaydediyoruz
                session["username"] = username  # Kullanıcı adını oturumda saklıyoruz

                return redirect(url_for("index"))  # Ana sayfaya yönlendiriyoruz
            else:
                flash("Parolanızı Yanlış Girdiniz...", "danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle Bir Kullanıcı Bulunmuyor...", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)
# Detay sayfası
@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")


# Çıkış işlemi
@app.route("/logout")
def logout():
    session.clear()  # Oturumu temizliyoruz
    flash("Başarıyla Çıkış yaptınız...", "info")  # Çıkış mesajı
    return redirect(url_for("index"))  # Ana sayfaya yönlendiriyoruz

#Makale ekleme
@app.route("/addarticle",methods = ["GET","POST"])
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content))

        mysql.connection.commit()

        cursor.close

        flash("Makale Başarıyla Eklendi","success")

        return redirect(url_for("dashboard"))
    
    return render_template("addarticle.html", form = form)

#Makale Silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where id = %s"

        cursor.execute(sorgu2,(id,))

        mysql.connection.commit()
        flash("Makale başarıyla silindi","success")
        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("index"))

#Makale Güncelle
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
    #GET request alırsak
    if request.method == "GET":
        cursor = mysql.connection.cursor()

        sorgu = "Select * from articles where id = %s and author = %s"
        result = cursor.execute(sorgu,(id,session["username"]))
        
        if result == 0:
            flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
            return redirect(url_for("index"))
        else:
            article = cursor.fetchone()
            form = ArticleForm()
            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html",form = form)
        
    #POST request alırsak    
    else:
        form = ArticleForm(request.form)

        newtitle = form.title.data
        newcontent = form.content.data

        sorgu2 = "Update articles Set title = %s,content = %s where id = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(sorgu2,(newtitle,newcontent,id))
        mysql.connection.commit()

        flash("Makale başarıyla güncellendi","success")
        return redirect(url_for("dashboard"))
#Makale Formu
class ArticleForm(Form):
    title = StringField("Makale Başlığı",validators=[validators.length(min=5,max=100)])
    content = TextAreaField("Makale İçeriği",validators=[validators.length(min=10)])

# Arama Url'si
@app.route("/search",methods = ["GET","POST"])
def search():
    if request.method == "GET":
        return redirect(url_for("index"))
    else:
        keyword = request.form.get("keyword")

        cursor = mysql.connection.cursor()

        sorgu = "Select * from articles where title like '%" + keyword +"%' "

        result = cursor.execute(sorgu)

        if result == 0:
            flash("Aranan kelimeye uygun makale bulunamadı","warning")
            return redirect(url_for("articles"))
        else: 
            articles = cursor.fetchall()

            return render_template("articles.html", articles = articles)


# Uygulama çalıştırılıyor
if __name__ == "__main__":
    app.run(debug=True)
