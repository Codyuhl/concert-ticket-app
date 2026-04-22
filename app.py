import os
from datetime import datetime
from decimal import Decimal

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

database_url = os.getenv("DATABASE_URL", "sqlite:///concerts.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# Database Models
# =========================

class Artist(db.Model):
    __tablename__ = "artist"

    artist_id = db.Column(db.Integer, primary_key=True)
    artist_name = db.Column(db.String(100), nullable=False, unique=True)
    genre = db.Column(db.String(50), nullable=False)

    concerts = db.relationship("Concert", backref="artist", lazy=True)

    def __repr__(self) -> str:
        return f"<Artist {self.artist_name}>"


class Venue(db.Model):
    __tablename__ = "venue"

    venue_id = db.Column(db.Integer, primary_key=True)
    venue_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    concerts = db.relationship("Concert", backref="venue", lazy=True)

    def __repr__(self) -> str:
        return f"<Venue {self.venue_name}>"


class Customer(db.Model):
    __tablename__ = "customer"

    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)

    tickets = db.relationship("Ticket", backref="customer", lazy=True)

    def __repr__(self) -> str:
        return f"<Customer {self.customer_name}>"


class Concert(db.Model):
    __tablename__ = "concert"

    concert_id = db.Column(db.Integer, primary_key=True)
    concert_date = db.Column(db.Date, nullable=False)

    artist_id = db.Column(db.Integer, db.ForeignKey("artist.artist_id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.venue_id"), nullable=False)

    tickets = db.relationship("Ticket", backref="concert", lazy=True)

    def __repr__(self) -> str:
        return f"<Concert {self.concert_id}>"


class Ticket(db.Model):
    __tablename__ = "ticket"

    ticket_id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    concert_id = db.Column(db.Integer, db.ForeignKey("concert.concert_id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"), nullable=False)

    def __repr__(self) -> str:
        return f"<Ticket {self.ticket_id}>"


# =========================
# Seed Data
# =========================

def seed_data() -> None:
    """Populate starter records only if the database is empty."""
    if Artist.query.first():
        return

    artist_1 = Artist(artist_name="Taylor Swift", genre="Pop")
    artist_2 = Artist(artist_name="Metallica", genre="Metal")

    venue_1 = Venue(venue_name="Madison Square Garden", city="New York", capacity=20000)
    venue_2 = Venue(venue_name="United Center", city="Chicago", capacity=23500)

    customer_1 = Customer(customer_name="Alice Johnson")
    customer_2 = Customer(customer_name="Bob Smith")

    db.session.add_all([artist_1, artist_2, venue_1, venue_2, customer_1, customer_2])
    db.session.commit()

    concert_1 = Concert(
        concert_date=datetime.strptime("2026-05-01", "%Y-%m-%d").date(),
        artist_id=artist_1.artist_id,
        venue_id=venue_1.venue_id,
    )
    concert_2 = Concert(
        concert_date=datetime.strptime("2026-06-15", "%Y-%m-%d").date(),
        artist_id=artist_2.artist_id,
        venue_id=venue_2.venue_id,
    )

    db.session.add_all([concert_1, concert_2])
    db.session.commit()

    ticket_1 = Ticket(
        seat_number="A12",
        price=Decimal("150.00"),
        concert_id=concert_1.concert_id,
        customer_id=customer_1.customer_id,
    )
    ticket_2 = Ticket(
        seat_number="B20",
        price=Decimal("95.50"),
        concert_id=concert_2.concert_id,
        customer_id=customer_2.customer_id,
    )

    db.session.add_all([ticket_1, ticket_2])
    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


# =========================
# Routes
# =========================

@app.route("/")
def home():
    return render_template("home.html")


# 1) Add Artist
@app.route("/add_artist", methods=["GET", "POST"])
def add_artist():
    if request.method == "POST":
        artist_name = request.form["artist_name"].strip()
        genre = request.form["genre"].strip()

        if not artist_name or not genre:
            flash("Artist name and genre are required.", "error")
            return redirect(url_for("add_artist"))

        existing_artist = Artist.query.filter(
            func.lower(Artist.artist_name) == artist_name.lower()
        ).first()
        if existing_artist:
            flash("Artist already exists.", "error")
            return redirect(url_for("add_artist"))

        new_artist = Artist(artist_name=artist_name, genre=genre)
        db.session.add(new_artist)
        db.session.commit()

        flash("Artist added successfully.", "success")
        return redirect(url_for("add_artist"))

    artists = Artist.query.order_by(Artist.artist_name).all()
    return render_template("add_artist.html", artists=artists)


# Bonus support: Add Venue
@app.route("/add_venue", methods=["GET", "POST"])
def add_venue():
    if request.method == "POST":
        venue_name = request.form["venue_name"].strip()
        city = request.form["city"].strip()
        capacity_raw = request.form["capacity"].strip()

        if not venue_name or not city or not capacity_raw:
            flash("All fields are required.", "error")
            return redirect(url_for("add_venue"))

        try:
            capacity = int(capacity_raw)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            flash("Capacity must be a positive integer.", "error")
            return redirect(url_for("add_venue"))

        new_venue = Venue(venue_name=venue_name, city=city, capacity=capacity)
        db.session.add(new_venue)
        db.session.commit()

        flash("Venue added successfully.", "success")
        return redirect(url_for("add_venue"))

    venues = Venue.query.order_by(Venue.city, Venue.venue_name).all()
    return render_template("add_venue.html", venues=venues)


# 2) Add Concert
@app.route("/add_concert", methods=["GET", "POST"])
def add_concert():
    artists = Artist.query.order_by(Artist.artist_name).all()
    venues = Venue.query.order_by(Venue.city, Venue.venue_name).all()

    if request.method == "POST":
        artist_id = request.form["artist_id"].strip()
        venue_id = request.form["venue_id"].strip()
        concert_date_raw = request.form["concert_date"].strip()

        if not artist_id or not venue_id or not concert_date_raw:
            flash("All fields are required.", "error")
            return redirect(url_for("add_concert"))

        try:
            concert_date = datetime.strptime(concert_date_raw, "%Y-%m-%d").date()
        except ValueError:
            flash("Concert date must be a valid date.", "error")
            return redirect(url_for("add_concert"))

        new_concert = Concert(
            artist_id=int(artist_id),
            venue_id=int(venue_id),
            concert_date=concert_date,
        )
        db.session.add(new_concert)
        db.session.commit()

        flash("Concert added successfully.", "success")
        return redirect(url_for("add_concert"))

    concerts = Concert.query.order_by(Concert.concert_date).all()
    return render_template(
        "add_concert.html",
        artists=artists,
        venues=venues,
        concerts=concerts,
    )


# 3) Add Customer
@app.route("/add_customer", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        customer_name = request.form["customer_name"].strip()

        if not customer_name:
            flash("Customer name is required.", "error")
            return redirect(url_for("add_customer"))

        new_customer = Customer(customer_name=customer_name)
        db.session.add(new_customer)
        db.session.commit()

        flash("Customer added successfully.", "success")
        return redirect(url_for("add_customer"))

    customers = Customer.query.order_by(Customer.customer_name).all()
    return render_template("add_customer.html", customers=customers)


# 4) Add Ticket Purchase
@app.route("/add_ticket", methods=["GET", "POST"])
def add_ticket():
    concerts = Concert.query.order_by(Concert.concert_date).all()
    customers = Customer.query.order_by(Customer.customer_name).all()

    if request.method == "POST":
        concert_id = request.form["concert_id"].strip()
        customer_id = request.form["customer_id"].strip()
        seat_number = request.form["seat_number"].strip()
        price_raw = request.form["price"].strip()

        if not concert_id or not customer_id or not seat_number or not price_raw:
            flash("All fields are required.", "error")
            return redirect(url_for("add_ticket"))

        try:
            price = Decimal(price_raw)
            if price < 0:
                raise ValueError
        except Exception:
            flash("Price must be a valid non-negative number.", "error")
            return redirect(url_for("add_ticket"))

        new_ticket = Ticket(
            concert_id=int(concert_id),
            customer_id=int(customer_id),
            seat_number=seat_number,
            price=price,
        )
        db.session.add(new_ticket)
        db.session.commit()

        flash("Ticket purchase added successfully.", "success")
        return redirect(url_for("add_ticket"))

    tickets = Ticket.query.order_by(Ticket.ticket_id.desc()).all()
    return render_template(
        "add_ticket.html",
        concerts=concerts,
        customers=customers,
        tickets=tickets,
    )


# 5) View all concerts and/or all concerts for a given city
@app.route("/view_concerts", methods=["GET", "POST"])
def view_concerts():
    cities = db.session.query(Venue.city).distinct().order_by(Venue.city).all()
    city_values = [row[0] for row in cities]

    selected_city = ""
    query = db.session.query(Concert).join(Artist).join(Venue)

    if request.method == "POST":
        selected_city = request.form.get("city", "").strip()
        if selected_city:
            query = query.filter(Venue.city == selected_city)

    concerts = query.order_by(Concert.concert_date).all()
    return render_template(
        "view_concerts.html",
        concerts=concerts,
        cities=city_values,
        selected_city=selected_city,
    )


# 6) View all concerts for a given artist
@app.route("/artist_concerts", methods=["GET", "POST"])
def artist_concerts():
    artists = Artist.query.order_by(Artist.artist_name).all()
    selected_artist_id = ""
    results = []

    if request.method == "POST":
        selected_artist_id = request.form["artist_id"].strip()
        if selected_artist_id:
            results = (
                db.session.query(
                    Artist.artist_name,
                    Venue.venue_name,
                    Venue.city,
                    Concert.concert_date,
                )
                .join(Concert, Artist.artist_id == Concert.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .filter(Artist.artist_id == int(selected_artist_id))
                .order_by(Concert.concert_date)
                .all()
            )

    return render_template(
        "artist_concerts.html",
        artists=artists,
        results=results,
        selected_artist_id=selected_artist_id,
    )


# 7) View total spending per customer
@app.route("/customer_spending", methods=["GET", "POST"])
def customer_spending():
    customers = Customer.query.order_by(Customer.customer_name).all()
    selected_customer_id = ""

    query = (
        db.session.query(
            Customer.customer_id,
            Customer.customer_name,
            func.coalesce(func.sum(Ticket.price), 0).label("total_spent"),
        )
        .outerjoin(Ticket, Customer.customer_id == Ticket.customer_id)
        .group_by(Customer.customer_id, Customer.customer_name)
        .order_by(Customer.customer_name)
    )

    if request.method == "POST":
        selected_customer_id = request.form.get("customer_id", "").strip()
        if selected_customer_id:
            query = query.filter(Customer.customer_id == int(selected_customer_id))

    spending = query.all()
    return render_template(
        "customer_spending.html",
        customers=customers,
        spending=spending,
        selected_customer_id=selected_customer_id,
    )


# 8) Top 3 artists whose concerts generated the highest total ticket revenue
@app.route("/top_artists")
def top_artists():
    results = (
        db.session.query(
            Artist.artist_name,
            func.coalesce(func.sum(Ticket.price), 0).label("total_revenue"),
        )
        .join(Concert, Artist.artist_id == Concert.artist_id)
        .outerjoin(Ticket, Concert.concert_id == Ticket.concert_id)
        .group_by(Artist.artist_id, Artist.artist_name)
        .order_by(func.coalesce(func.sum(Ticket.price), 0).desc(), Artist.artist_name)
        .limit(3)
        .all()
    )
    return render_template("top_artists.html", results=results)


# 9) Bonus: venue performance report
@app.route("/venue_report")
def venue_report():
    results = (
        db.session.query(
            Venue.venue_name,
            Venue.city,
            Venue.capacity,
            func.count(func.distinct(Concert.concert_id)).label("num_concerts"),
            func.count(Ticket.ticket_id).label("tickets_sold"),
            func.coalesce(func.sum(Ticket.price), 0).label("total_revenue"),
            func.coalesce(func.avg(Ticket.price), 0).label("avg_ticket_price"),
        )
        .outerjoin(Concert, Venue.venue_id == Concert.venue_id)
        .outerjoin(Ticket, Concert.concert_id == Ticket.concert_id)
        .group_by(Venue.venue_id, Venue.venue_name, Venue.city, Venue.capacity)
        .order_by(func.coalesce(func.sum(Ticket.price), 0).desc(), Venue.venue_name)
        .all()
    )
    return render_template("venue_report.html", results=results)


@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(debug=True)
