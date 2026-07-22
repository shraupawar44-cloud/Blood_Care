from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "bloodcare123"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db():

    conn = sqlite3.connect("blood.db")
    conn.row_factory = sqlite3.Row

    return conn



# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():

    return render_template("index.html")



# -----------------------------
# REGISTER DONOR
# -----------------------------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        blood_group = request.form["blood_group"]
        city = request.form["city"]
        phone = request.form["phone"]
        availability = request.form["availability"]


        conn = get_db()
        cursor = conn.cursor()


        cursor.execute("""
        INSERT INTO donors
        (name,email,password,blood_group,city,phone,availability)

        VALUES(?,?,?,?,?,?,?)
        """,
        (
            name,
            email,
            password,
            blood_group,
            city,
            phone,
            availability
        ))


        conn.commit()
        conn.close()


        return redirect("/login")


    return render_template("register.html")




# -----------------------------
# DONOR LOGIN
# -----------------------------
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":


        phone=request.form["phone"]
        password = request.form["password"]


        conn = get_db()
        cursor = conn.cursor()


        cursor.execute(
        """
        SELECT * FROM donors
        WHERE phone=? AND password=?
        """,
        (
            phone,
            password
        ))


        user = cursor.fetchone()

        conn.close()



        if user:


            session["user_id"] = user["id"]


            return redirect("/dashboard")


        else:

            return render_template(
            "login.html",
            error="Invalid phone or Password"
            )



    return render_template("login.html")





# -----------------------------
# DONOR DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():


    if "user_id" not in session:

        return redirect("/login")



    conn = get_db()

    cursor = conn.cursor()


    cursor.execute(
    """
    SELECT * FROM donors
    WHERE id=?
    """,
    (
        session["user_id"],
    ))


    donor = cursor.fetchone()


    conn.close()


    return render_template(
        "dashboard.html",
        donor=donor
    )





# -----------------------------
# UPDATE DONOR STATUS
# -----------------------------
@app.route("/update_status", methods=["POST"])
def update_status():


    if "user_id" not in session:

        return redirect("/login")



    status = request.form["availability"]



    conn = get_db()

    cursor = conn.cursor()



    cursor.execute(
    """
    UPDATE donors
    SET availability=?
    WHERE id=?
    """,
    (
        status,
        session["user_id"]
    ))



    conn.commit()

    conn.close()



    return redirect("/dashboard")





# -----------------------------
# SEARCH DONOR
# -----------------------------
@app.route("/search", methods=["GET","POST"])
def search():


    if request.method == "POST":


        blood = request.form["blood_group"]

        city = request.form["city"]



        conn = get_db()

        cursor = conn.cursor()



        cursor.execute(
        """
        SELECT name,blood_group,city,phone,availability

        FROM donors

        WHERE blood_group=?

        AND city=?

        AND availability='Available'
        """,
        (
            blood,
            city
        ))



        donors = cursor.fetchall()


        conn.close()



        return render_template(
            "result.html",
            donors=donors
        )



    return render_template("search.html")







# -----------------------------
# ADMIN LOGIN
# -----------------------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        print(username, password)   # for checking


        if username == "admin" and password == "admin123":

            session["admin"] = "admin"
            return redirect("/admin")


        else:

            return render_template(
                "admin_login.html",
                error="Invalid Admin Credentials"
            )


    return render_template("admin_login.html")



# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/admin")
def admin():

    if session.get("admin") != "admin":
        return redirect("/admin_login")


    conn=get_db()
    cursor=conn.cursor()

    cursor.execute("SELECT * FROM donors")

    donors=cursor.fetchall()

    conn.close()


    return render_template(
        "admin.html",
        donors=donors
    )


# -----------------------------
# ADMIN LOGOUT
# -----------------------------
@app.route("/admin_logout")
def admin_logout():

    session.clear()

    return redirect("/admin_login")


# -----------------------------
# DONOR LOGOUT
# -----------------------------
@app.route("/logout")
def logout():


    session.clear()


    return redirect("/")







# -----------------------------
# RUN APP
# -----------------------------
if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )