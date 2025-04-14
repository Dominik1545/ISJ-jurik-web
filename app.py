from flask import Flask, request
import sqlite3
import hashlib

app = Flask(__name__)

def pripoj_db():
    conn = sqlite3.connect("kurzy.db")
    return conn

# Afinná šifra (A=5, B=8)
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
    return '''
        <h1>Výber z databázy</h1>
        <a href="/kurzy"><button type="button">Zobraz všetky kurzy</button></a>
        <a href="/treneri"><button type="button">Zobraz všetkých trénerov</button></a>
        <a href="/miesta"><button type="button">Zobraz miesta</button></a>
        <a href="/kapacita"><button type="button">Zobraz kapacitu</button></a>
        <a href="/registracia"><button type="button">Registruj trénera</button></a>
        <a href="/pridaj_kurz"><button type="button">Pridaj nový kurz</button></a>
        <hr>
    '''

@app.route('/kurzy')
def zobraz_kurzy():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Kurzy")
    kurzy = cursor.fetchall()
    conn.close()

    vystup = "<h2>Zoznam kurzov:</h2>"
    for kurz in kurzy:
        vystup += f"<p>{kurz}</p>"
    vystup += '<br><a href="/"><button type="button">Späť</button></a>'
    return vystup

@app.route('/treneri')
def zobraz_trenerov():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT T.ID_trenera, T.Meno || ' ' || T.Priezvisko as Trener, 
               IFNULL(Nazov_kurzu, 'Žiadny kurz') 
        FROM Treneri T 
        LEFT JOIN Kurzy K ON T.ID_trenera = K.ID_trenera
    """)
    treneri = cursor.fetchall()
    conn.close()

    vystup = "<h2>Zoznam trénerov a kurzov:</h2>"
    for trener in treneri:
        vystup += f"<p>{trener[1]} - {trener[2]}</p>"
    vystup += '<br><a href="/"><button type="button">Späť</button></a>'
    return vystup

@app.route('/miesta')
def zobraz_miesta():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Nazov_miesta FROM Miesta")
    miesta = cursor.fetchall()
    conn.close()

    vystup = "<h2>Zoznam miest:</h2>"
    for miesto in miesta:
        vystup += f"<p>{miesto[0]}</p>"
    vystup += '<br><a href="/"><button type="button">Späť</button></a>'
    return vystup

@app.route('/kapacita')
def zobraz_kapacitu():
    conn = pripoj_db()
    cursor = conn.cursor()
    cursor.execute("SELECT Nazov_kurzu, Max_pocet_ucastnikov FROM Kurzy")
    kapacity = cursor.fetchall()
    conn.close()

    vystup = "<h2>Kapacity kurzov:</h2>"
    for kurz in kapacity:
        vystup += f"<p>{kurz[0]} - Kapacita: {kurz[1]}</p>"
    vystup += '<br><a href="/"><button type="button">Späť</button></a>'
    return vystup

@app.route('/registracia', methods=['GET', 'POST'])
def registracia():
    if request.method == 'POST':
        meno = request.form['meno']
        priezvisko = request.form['priezvisko']
        specializacia = request.form['specializacia']
        telefon = request.form['telefon']
        heslo = request.form['heslo']
        heslo_hash = hashlib.sha256(heslo.encode()).hexdigest()

        conn = pripoj_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Treneri (Meno, Priezvisko, Specializacia, Telefon, Heslo) VALUES (?, ?, ?, ?, ?)", 
                       (meno, priezvisko, specializacia, telefon, heslo_hash))
        conn.commit()
        conn.close()

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
        kapacita = request.form['kapacita']
        trener_id = request.form['trener_id']

        # Šifrovanie textových údajov
        nazov_sifrovany = afinne_sifrovanie(nazov)
        typ_sifrovany = afinne_sifrovanie(typ)

        conn = pripoj_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Kurzy (Nazov_kurzu, Typ_sportu, Max_pocet_ucastnikov, ID_trenera) VALUES (?, ?, ?, ?)", 
                       (nazov_sifrovany, typ_sifrovany, kapacita, trener_id))
        conn.commit()
        conn.close()

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
    app.run(debug=True)







