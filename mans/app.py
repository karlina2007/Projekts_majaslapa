from flask import Flask, render_template, request
import sqlite3, requests, random

## izveidojas datubaze ja ta jau neeksiste
app = Flask(__name__)
DB = "gramatas.db"
def izveido_datubazi():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS gramatas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nosaukums TEXT,
            autors TEXT,
            apraksts TEXT
        )
    """)
    conn.commit()
    conn.close()

izveido_datubazi()



### Lietotaja ierakstītos datus pievieno/iemet datubāzē
def pievienot(nosaukums, autors, apraksts):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("INSERT INTO gramatas (nosaukums, autors, apraksts) VALUES (?, ?, ?)",
              (nosaukums, autors, apraksts))
    conn.commit()
    conn.close()

# Lietotāja ievadītā grāmata tiek dzēsta(lietotajs ievada gramatas nosaukumu to kas ir tabula. Ta ir funkcija kuru velak pievieno lapai)
def dzest(nosaukums):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM gramatas WHERE nosaukums = ?", (nosaukums,))
    conn.commit()
    conn.close()

#### Dati tiek paņemti lai pec tam viņus paraditu
def dabut_gramatas():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT nosaukums, autors, apraksts FROM gramatas")
    dati = c.fetchall()
    conn.close()
    return dati


####pirma lappuse ar tabulu
@app.route("/")
def index():
    gramatas = dabut_gramatas()
    return render_template("index.html", gramatas=gramatas)


##otra lapa- pievienot gramatu
@app.route("/pievienot", methods=["GET", "POST"])
def pievienot_lapa():

    if request.method == "POST":
        nosaukums = request.form.get("nosaukums")
        autors = request.form.get("autors")
        apraksts = request.form.get("apraksts")
        if nosaukums:
            pievienot(nosaukums, autors, apraksts)
            f"Pievienots"

    return render_template("pievienot.html")


#treša lapa route(dzešanas lapa)


@app.route("/dzest", methods=["GET", "POST"])
def dzest_lapa():
    atb =""
    if request.method == "POST":
        nosaukums = request.form.get("nosaukums")
        if nosaukums:
            dzest(nosaukums)
            atb = "Grāmata ar ievadīto nosaukumu ir dzēsta."
        else:
            atb = "Ievadi nosaukumu!"
    return render_template("dzest.html", atb=atb)




##lapa ar api ņem grāmatas no google books
@app.route("/random")
def nejauša():
    try:
        kategorijas = ["fiction", "history", "romance", "science"]
        tema = random.choice(kategorijas)
        url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{tema}&maxResults=10"
        dati = requests.get(url, timeout=4).json()
        gr = random.choice(dati["items"])["volumeInfo"]
        nosaukums = gr.get("title", "Bez nosaukuma")
        autors = ", ".join(gr.get("authors", ["Nezināms autors"]))
        apraksts = gr.get("description", "Apraksts nav pieejams.")

    except:
        nosaukums, autors, apraksts = "Nav apraksta", "", ""
    return render_template("random.html", nosaukums=nosaukums, autors=autors, apraksts=apraksts)

# palaiž/atjauno automatiski
if __name__ == "__main__":
    app.run(debug=True)
