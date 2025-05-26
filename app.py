from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os

from flask import g, session
from i18n import TRANSLATIONS, SUPPORTED

app = Flask(__name__, instance_relative_config=True)
app.secret_key = "tajny_kluc"
os.makedirs(app.instance_path, exist_ok=True)


db_path = os.path.join(app.instance_path, "kurzy.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}".replace("\\", "/")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.before_request
def set_lang():
    lang = request.args.get("lang")
    if lang not in SUPPORTED:
        lang = session.get("lang","sk")
    session["lang"] = lang
    g.t = TRANSLATIONS[lang]

@app.context_processor
def inject_translations():
    return dict(t=g . t)

class Trener(db.Model):
    __tablename__ = "Treneri"

    ID_trenera = db.Column(db.Integer, primary_key=True)
    Meno = db.Column(db.String, nullable=False)
    Priezvisko = db.Column(db.String, nullable=False)
    Specializacia = db.Column(db.String)
    Telefon = db.Column(db.String)
    Heslo = db.Column(db.String)

    kurzy = db.relationship('Kurz', backref='trener', lazy=True)

class Kurz(db.Model):
    __tablename__ = "Kurzy"

    ID_kurzu = db.Column(db.Integer, primary_key=True)
    Nazov_kurzu = db.Column(db.String, nullable=False)
    Typ_sportu = db.Column(db.String)
    Max_pocet_ucastnikov = db.Column(db.Integer)
    ID_trenera = db.Column(db.Integer, db.ForeignKey('Treneri.ID_trenera'))

    def __repr__(self):
        return f"<Kurz {self.Nazov_kurzu}>"

class Miesto(db.Model):
    __tablename__ = "Miesta"

    ID_miesta = db.Column(db.Integer, primary_key=True)
    Nazov_miesta = db.Column(db.String, nullable=False)


def afinne_sifrovanie(text):
    vysledok = ''
    for znak in text:
        if znak.isalpha():
            zaklad = ord('A') if znak.isupper() else ord('a')
            posun = (5 * (ord(znak) - zaklad) + 8) % 26
            vysledok += chr(zaklad + posun)
        else:
            vysledok += znak
    return vysledok


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/kurzy')
def zobraz_kurzy():
    kurzy = Kurz.query.all()
    return render_template("kurzy.html", kurzy=kurzy)

@app.route('/treneri')
def zobraz_trenerov():
    treneri = Trener.query.all()
    return render_template("treneri.html", treneri=treneri)


@app.route('/miesta')
def zobraz_miesta():
    miesta = Miesto.query.all()
    return render_template("miesta.html", miesta=miesta)


@app.route('/kapacity')
@app.route('/kapacita')
def vypis_kapacity():
    kurzy = Kurz.query.with_entities(Kurz.Nazov_kurzu, Kurz.Max_pocet_ucastnikov).filter(Kurz.Nazov_kurzu.like('P%')).all()
    return render_template("kapacity.html", kapacity=kurzy)




@app.route('/registracia', methods=['GET', 'POST'])
def registracia():
    if request.method == 'POST':
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        specializacia = request.form['specializacia']
        telefon = request.form['telefon']
        heslo = request.form['heslo']
        heslo_hash = hashlib.sha256(heslo.encode()).hexdigest()

        novy_trener = Trener(
            Meno=meno,
            Priezvisko=priezvisko,
            Specializacia=specializacia,
            Telefon=telefon,
            Heslo=heslo_hash
        )
        db.session.add(novy_trener)
        db.session.commit()

        return '''
            <h2>Tréner bol úspešne zaregistrovaný!</h2>
            <hr>
            <a href="/"><button type="button">Späť</button></a>
        '''
    return '''
        <h2>Registrácia trénera</h2>
        <form action="/registracia" method="post">
            <label>Meno:</label><br>
            <input type="text" name="meno" required><br><br>
            <label>Priezvisko:</label><br>
            <input type="text" name="priezvisko" required><br><br>
            <label>Špecializácia:</label><br>
            <input type="text" name="specializacia" required><br><br>
            <label>Telefón:</label><br>
            <input type="text" name="telefon" required><br><br>
            <label>Heslo:</label><br>
            <input type="password" name="heslo" required><br><br>
            <button type="submit">Registrovať</button>
        </form>
        <hr>
        <a href="/"><button type="button">Späť</button></a>
    '''

@app.route('/pridaj_kurz', methods=['GET', 'POST'])
def pridaj_kurz():
    if request.method == 'POST':
        nazov = request.form['nazov']
        typ = request.form['typ']
        kapacita = int(request.form['kapacita'])
        trener_id = int(request.form['trener_id'])

        kurz = Kurz(
            Nazov_kurzu=afinne_sifrovanie(nazov),
            Typ_sportu=afinne_sifrovanie(typ),
            Max_pocet_ucastnikov=kapacita,
            ID_trenera=trener_id
        )
        db.session.add(kurz)
        db.session.commit()

        return '''
            <h2>Kurz bol úspešne pridaný!</h2>
            <a href="/"><button type="button">Späť</button></a>
        '''
    return '''
        <h2>Pridanie nového kurzu</h2>
        <form method="post">
            <label>Názov kurzu:</label><br>
            <input type="text" name="nazov" required><br><br>
            <label>Typ športu:</label><br>
            <input type="text" name="typ" required><br><br>
            <label>Max. počet účastníkov:</label><br>
            <input type="number" name="kapacita" required><br><br>
            <label>ID trénera:</label><br>
            <input type="number" name="trener_id" required><br><br>
            <button type="submit">Pridať kurz</button>
        </form>
        <hr>
        <a href="/"><button type="button">Späť</button></a>
    '''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
