from flask import Flask, render_template, abort, url_for, request, redirect, session
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tourisme_fr"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF"}
DB_PATH = os.path.join(os.path.dirname(__file__), "bookings.db")

SUPPORTED_LANGS = ["fr", "en", "de"]

UI = {
    "fr": {
        "nav_home": "Accueil",
        "nav_contact": "Contact / Réservation",
        "nav_tarifs": "Nos tarifs",
        "cta_contact": "Contact / Réservation",
        "cta_tarifs": "Nos tarifs",
        "home_title": "Nos 11 régions en images",
        "home_intro_title": "Bienvenue au Sud du Maroc",
        "home_intro_text": "Entre océan, montagnes et désert, découvre des expériences authentiques : balades, patrimoine, cuisine, sensations fortes et paysages à couper le souffle.",
        "region_about": "À propos",
        "region_photos": "Photos",
        "reserve": "Réserver",
        "back": "Retour",
        "contact_title": "Demande de réservation",
        "contact_sub": "Réponse rapide par téléphone ou email.",
        "sent_ok": "Message envoyé ✅",
        "sent_ok_sub": "On te recontacte dès que possible.",
        "f_name": "Nom",
        "f_email": "Email",
        "f_phone": "Téléphone",
        "f_region": "Région / Ville",
        "f_date_from": "Date (de)",
        "f_date_to": "Date (à)",
        "f_people": "Voyageurs",
        "f_activities": "Activités",
        "f_message": "Message",
        "send": "Envoyer",
        "payment": "Paiement",
        "payment_note": "Placeholder visuel (connexion banque plus tard).",
        "pay_paypal": "Payer (PayPal) — placeholder",
        "tarifs_title": "Nos tarifs",
        "tarifs_sub": "Clair, simple, organisé.",
        "t_exp": "Expérience",
        "t_duree": "Durée",
        "t_prix": "Prix",
        "t_details": "Détails",
        "footer_contact": "Adresse : Nehda Lkobra double voie · Téléphone : +41 79 558 15 41 · Email : robot.comptable@gmail.com · WhatsApp : +41 79 558 15 41",
    },
    "en": {
        "nav_home": "Home",
        "nav_contact": "Contact / Booking",
        "nav_tarifs": "Prices",
        "cta_contact": "Contact / Booking",
        "cta_tarifs": "Prices",
        "home_title": "Our 11 regions in pictures",
        "home_intro_title": "Welcome to Southern Morocco",
        "home_intro_text": "Between the Atlantic, the mountains and the desert, enjoy authentic experiences: culture, local cuisine, thrilling rides and breathtaking landscapes.",
        "region_about": "About",
        "region_photos": "Photos",
        "reserve": "Book now",
        "back": "Back",
        "contact_title": "Booking request",
        "contact_sub": "Fast reply by phone or email.",
        "sent_ok": "Message sent ✅",
        "sent_ok_sub": "We will get back to you as soon as possible.",
        "f_name": "Name",
        "f_email": "Email",
        "f_phone": "Phone",
        "f_region": "Region / City",
        "f_date_from": "From",
        "f_date_to": "To",
        "f_people": "Guests",
        "f_activities": "Activities",
        "f_message": "Message",
        "send": "Send",
        "payment": "Payment",
        "payment_note": "Visual placeholder (bank connection later).",
        "pay_paypal": "Pay (PayPal) — placeholder",
        "tarifs_title": "Prices",
        "tarifs_sub": "Clear, simple, organized.",
        "t_exp": "Experience",
        "t_duree": "Duration",
        "t_prix": "Price",
        "t_details": "Details",
        "footer_contact": "Address: Nehda Lkobra double voie · Phone: +41 79 558 15 41 · Email: robot.comptable@gmail.com · WhatsApp: +41 79 558 15 41",
    },
    "de": {
        "nav_home": "Start",
        "nav_contact": "Kontakt / Buchung",
        "nav_tarifs": "Preise",
        "cta_contact": "Kontakt / Buchung",
        "cta_tarifs": "Preise",
        "home_title": "Unsere 11 Regionen in Bildern",
        "home_intro_title": "Willkommen im Süden Marokkos",
        "home_intro_text": "Zwischen Atlantik, Bergen und Wüste erwarten dich authentische Erlebnisse: Kultur, lokale Küche, Abenteuer und atemberaubende Landschaften.",
        "region_about": "Über",
        "region_photos": "Fotos",
        "reserve": "Jetzt buchen",
        "back": "Zurück",
        "contact_title": "Buchungsanfrage",
        "contact_sub": "Schnelle Antwort per Telefon oder E-Mail.",
        "sent_ok": "Nachricht gesendet ✅",
        "sent_ok_sub": "Wir melden uns so schnell wie möglich.",
        "f_name": "Name",
        "f_email": "E-Mail",
        "f_phone": "Telefon",
        "f_region": "Region / Stadt",
        "f_date_from": "Von",
        "f_date_to": "Bis",
        "f_people": "Personen",
        "f_activities": "Aktivitäten",
        "f_message": "Nachricht",
        "send": "Senden",
        "payment": "Zahlung",
        "payment_note": "Nur als Platzhalter (Bankanbindung später).",
        "pay_paypal": "Bezahlen (PayPal) — Platzhalter",
        "tarifs_title": "Preise",
        "tarifs_sub": "Klar, einfach, übersichtlich.",
        "t_exp": "Erlebnis",
        "t_duree": "Dauer",
        "t_prix": "Preis",
        "t_details": "Details",
        "footer_contact": "Adresse: Nehda Lkobra double voie · Telefon: +41 79 558 15 41 · E-Mail: robot.comptable@gmail.com · WhatsApp: +41 79 558 15 41",
    },
}

REGION_TEXTS = {
    "fr": {
        "agadir": "Agadir t’accueille entre l’Atlantique et la kasbah : une ville lumineuse, parfaite pour lancer l’aventure, goûter le terroir et vivre le sud à plein rythme.",
        "taghazout_village_colore": "Taghazout et ses villages colorés : ambiance surf, ruelles vivantes, panoramas océaniques et couchers de soleil qui donnent envie de rester.",
        "vallee_paradis": "La Vallée du Paradis : palmiers, bassins naturels et fraîcheur cachée dans l’Anti-Atlas — une parenthèse nature spectaculaire.",
        "cascade_immouzzar": "Immouzzar : routes panoramiques, cascades et nature authentique — l’escapade idéale pour respirer et explorer.",
        "timlaline": "Timlaline : dunes dorées, silence du désert et lumière incroyable — une expérience inoubliable, entre sable et horizon.",
        "petit_desert": "Le petit désert : une immersion saharienne accessible, parfaite pour l’adrénaline, les photos et la magie des dunes.",
        "tafraout": "Tafraout : roches roses, vallées sculptées et villages amazighs — un décor unique, sauvage et profondément marocain.",
        "tiznit": "Tiznit : médina, artisanat d’argent et charme du sud — une halte authentique entre histoire et savoir-faire.",
        "arches_igzira": "Legzira : falaises rouges, arches mythiques et océan puissant — un spot iconique qui impressionne à chaque pas.",
        "essaouira": "Essaouira : médina classée, air marin, art et musique — une ville douce, élégante et inspirante.",
        "marrakech": "Marrakech : souks, palais et jardins — une journée intense, colorée, et totalement inoubliable.",
    },
    "en": {
        "agadir": "Agadir welcomes you between the Atlantic and the old kasbah: bright, lively, and the perfect gateway to the South’s best experiences.",
        "taghazout_village_colore": "Taghazout and its colorful villages: surf vibes, ocean views, vibrant streets and unforgettable sunsets.",
        "vallee_paradis": "Paradise Valley: palm trees, natural pools and cool hidden spots in the Anti-Atlas — a breathtaking nature escape.",
        "cascade_immouzzar": "Imouzzer: scenic roads, waterfalls and authentic landscapes — the ideal day out to breathe and explore.",
        "timlaline": "Timlaline: golden dunes, desert silence and stunning light — a true Sahara-style moment near the coast.",
        "petit_desert": "The little desert: an accessible Sahara experience for adrenaline, photos, and the magic of the dunes.",
        "tafraout": "Tafraout: pink rocks, carved valleys and Amazigh villages — wild, unique and deeply Moroccan.",
        "tiznit": "Tiznit: a medina, silver craftsmanship and southern charm — a genuine stop between history and know-how.",
        "arches_igzira": "Legzira: red cliffs, legendary arches and a powerful ocean — an iconic place that leaves a mark.",
        "essaouira": "Essaouira: UNESCO medina, sea breeze, art and music — relaxed, elegant and inspiring.",
        "marrakech": "Marrakech: souks, palaces and gardens — a vibrant day packed with color and memories.",
    },
    "de": {
        "agadir": "Agadir liegt zwischen Atlantik und Kasbah: hell, lebendig und der perfekte Startpunkt für die Highlights des Südens.",
        "taghazout_village_colore": "Taghazout und seine bunten Dörfer: Surf-Feeling, Meeresblicke, lebhafte Gassen und unvergessliche Sonnenuntergänge.",
        "vallee_paradis": "Paradise Valley: Palmen, Naturbecken und kühle Oasen im Anti-Atlas — ein beeindruckender Natur-Ausflug.",
        "cascade_immouzzar": "Imouzzer: Panoramastraßen, Wasserfälle und authentische Landschaften — ideal zum Durchatmen und Entdecken.",
        "timlaline": "Timlaline: goldene Dünen, Wüstenstille und fantastisches Licht — ein Sahara-Moment nahe der Küste.",
        "petit_desert": "Die kleine Wüste: ein gut erreichbares Wüsten-Erlebnis für Action, Fotos und den Zauber der Dünen.",
        "tafraout": "Tafraout: rosafarbene Felsen, geformte Täler und Amazigh-Dörfer — wild, einzigartig und sehr marokkanisch.",
        "tiznit": "Tiznit: Medina, Silberschmuck und südlicher Charme — ein echter Halt zwischen Geschichte und Handwerk.",
        "arches_igzira": "Legzira: rote Klippen, legendäre Bögen und Atlantik-Power — ein ikonischer Ort, der beeindruckt.",
        "essaouira": "Essaouira: UNESCO-Medina, Meeresbrise, Kunst und Musik — entspannt, elegant und inspirierend.",
        "marrakech": "Marrakesch: Souks, Paläste und Gärten — ein intensiver Tag voller Farben und Eindrücke.",
    },
}

TARIFS = [
    {"cat_fr":"Agadir / Ville", "cat_en":"Agadir / City", "cat_de":"Agadir / Stadt", "title_fr":"Visite de ville d’Agadir", "title_en":"Agadir city tour", "title_de":"Stadttour Agadir", "duration_fr":"3h", "duration_en":"3h", "duration_de":"3 Std.", "price_fr":"14€ / personne", "price_en":"€14 / person", "price_de":"14€ / Person", "details_fr":"Kasbah, Marina, Jardin Olhao, Grande Mosquée, Souk", "details_en":"Kasbah, Marina, Olhao Garden, Grand Mosque, Souk", "details_de":"Kasbah, Marina, Olhao-Garten, Große Moschee, Souk"},
    {"cat_fr":"Agadir / Ville", "cat_en":"Agadir / City", "cat_de":"Agadir / Stadt", "title_fr":"Visite de ville + téléphérique", "title_en":"City tour + cable car", "title_de":"Stadttour + Seilbahn", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"27€ / personne", "price_en":"€27 / person", "price_de":"27€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Agadir / Ville", "cat_en":"Agadir / City", "cat_de":"Agadir / Stadt", "title_fr":"Médina de Coco Polizzi", "title_en":"Coco Polizzi Medina", "title_de":"Medina Coco Polizzi", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"20€ / personne", "price_en":"€20 / person", "price_de":"20€ / Person", "details_fr":"Entrée incluse", "details_en":"Entry included", "details_de":"Eintritt inklusive"},
    {"cat_fr":"Nature", "cat_en":"Nature", "cat_de":"Natur", "title_fr":"Vallée du Paradis", "title_en":"Paradise Valley", "title_de":"Paradise Valley", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"15€ / personne", "price_en":"€15 / person", "price_de":"15€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Nature", "cat_en":"Nature", "cat_de":"Natur", "title_fr":"Cascade Immouzzar", "title_en":"Imouzzer waterfall", "title_de":"Wasserfall Imouzzer", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"30€ / personne", "price_en":"€30 / person", "price_de":"30€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Villes / Régions", "cat_en":"Towns / Regions", "cat_de":"Städte / Regionen", "title_fr":"Taghazout & village coloré", "title_en":"Taghazout & colorful village", "title_de":"Taghazout & buntes Dorf", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"35€ / personne", "price_en":"€35 / person", "price_de":"35€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Villes / Régions", "cat_en":"Towns / Regions", "cat_de":"Städte / Regionen", "title_fr":"Timlaline", "title_en":"Timlaline dunes", "title_de":"Dünen Timlaline", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"35€ / personne", "price_en":"€35 / person", "price_de":"35€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Parcs", "cat_en":"Parks", "cat_de":"Parks", "title_fr":"Crocodile Parc", "title_en":"Crocodile Park", "title_de":"Krokodilpark", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"30€ / personne", "price_en":"€30 / person", "price_de":"30€ / Person", "details_fr":"Billet d’entrée inclus", "details_en":"Entry ticket included", "details_de":"Eintritt inklusive"},
    {"cat_fr":"Mer", "cat_en":"Sea", "cat_de":"Meer", "title_fr":"Balade en mer + pêche", "title_en":"Boat trip + fishing", "title_de":"Bootstour + Angeln", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"50€", "price_en":"€50", "price_de":"50€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Aventure", "cat_en":"Adventure", "cat_de":"Abenteuer", "title_fr":"Aventure Quad", "title_en":"Quad adventure", "title_de":"Quad-Abenteuer", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"40€", "price_en":"€40", "price_de":"40€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Aventure", "cat_en":"Adventure", "cat_de":"Abenteuer", "title_fr":"Aventure Buggy", "title_en":"Buggy adventure", "title_de":"Buggy-Abenteuer", "duration_fr":"Demi-journée", "duration_en":"Half-day", "duration_de":"Halbtags", "price_fr":"60€", "price_en":"€60", "price_de":"60€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Culture / Cuisine", "cat_en":"Culture / Food", "cat_de":"Kultur / Küche", "title_fr":"Cours de cuisine", "title_en":"Cooking class", "title_de":"Kochkurs", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"40€ / personne", "price_en":"€40 / person", "price_de":"40€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Désert", "cat_en":"Desert", "cat_de":"Wüste", "title_fr":"Balade dromadaire", "title_en":"Camel ride", "title_de":"Kamelritt", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"Adulte 20€ · Enfant 10€", "price_en":"Adult €20 · Child €10", "price_de":"Erw. 20€ · Kind 10€", "details_fr":"Option barbecue : Adulte 35€ · Enfant 25€", "details_en":"BBQ option: Adult €35 · Child €25", "details_de":"BBQ-Option: Erw. 35€ · Kind 25€"},
    {"cat_fr":"Mer", "cat_en":"Sea", "cat_de":"Meer", "title_fr":"Jet-ski aventure", "title_en":"Jet ski adventure", "title_de":"Jet-Ski-Abenteuer", "duration_fr":"30 min", "duration_en":"30 min", "duration_de":"30 Min.", "price_fr":"60€", "price_en":"€60", "price_de":"60€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Bien-être", "cat_en":"Wellness", "cat_de":"Wellness", "title_fr":"Hammam + massage", "title_en":"Hammam + massage", "title_de":"Hammam + Massage", "duration_fr":"2h", "duration_en":"2h", "duration_de":"2 Std.", "price_fr":"40€ / personne", "price_en":"€40 / person", "price_de":"40€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Soirée", "cat_en":"Evening show", "cat_de":"Abendshow", "title_fr":"Chems Ayour Fantasia", "title_en":"Chems Ayour Fantasia", "title_de":"Chems Ayour Fantasia", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"Adulte 55€ · Enfant 30€", "price_en":"Adult €55 · Child €30", "price_de":"Erw. 55€ · Kind 30€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Nature", "cat_en":"Nature", "cat_de":"Natur", "title_fr":"Parc national Souss Massa", "title_en":"Souss Massa National Park", "title_de":"Nationalpark Souss Massa", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"Adulte 70€ · Enfant 40€", "price_en":"Adult €70 · Child €40", "price_de":"Erw. 70€ · Kind 40€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Excursions", "cat_en":"Day trips", "cat_de":"Ausflüge", "title_fr":"Taroudant & oasis de Tiout", "title_en":"Taroudant & Tiout oasis", "title_de":"Taroudant & Oase Tiout", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"35€ / personne", "price_en":"€35 / person", "price_de":"35€ / Person", "details_fr":"Déjeuner inclus", "details_en":"Lunch included", "details_de":"Mittagessen inklusive"},
    {"cat_fr":"Excursions", "cat_en":"Day trips", "cat_de":"Ausflüge", "title_fr":"Tafraout & Tiznit", "title_en":"Tafraout & Tiznit", "title_de":"Tafraout & Tiznit", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"39€ / personne", "price_en":"€39 / person", "price_de":"39€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Excursions", "cat_en":"Day trips", "cat_de":"Ausflüge", "title_fr":"Arches de Legzira", "title_en":"Legzira arches", "title_de":"Legzira-Bögen", "duration_fr":"1 journée", "duration_en":"1 day", "duration_de":"1 Tag", "price_fr":"Adulte 60€ · Enfant 40€", "price_en":"Adult €60 · Child €40", "price_de":"Erw. 60€ · Kind 40€", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Excursions", "cat_en":"Day trips", "cat_de":"Ausflüge", "title_fr":"Marrakech", "title_en":"Marrakech", "title_de":"Marrakesch", "duration_fr":"1 journée", "duration_en":"1 day", "duration_de":"1 Tag", "price_fr":"50€ / personne", "price_en":"€50 / person", "price_de":"50€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Excursions", "cat_en":"Day trips", "cat_de":"Ausflüge", "title_fr":"Essaouira", "title_en":"Essaouira", "title_de":"Essaouira", "duration_fr":"1 journée", "duration_en":"1 day", "duration_de":"1 Tag", "price_fr":"40€ / personne", "price_en":"€40 / person", "price_de":"40€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Désert", "cat_en":"Desert", "cat_de":"Wüste", "title_fr":"Petit désert", "title_en":"Little desert", "title_de":"Kleine Wüste", "duration_fr":"—", "duration_en":"—", "duration_de":"—", "price_fr":"50€ / personne", "price_en":"€50 / person", "price_de":"50€ / Person", "details_fr":"", "details_en":"", "details_de":""},
    {"cat_fr":"Circuit", "cat_en":"Tour", "cat_de":"Rundreise", "title_fr":"2 jours Agadir → Essaouira → Marrakech", "title_en":"2 days Agadir → Essaouira → Marrakech", "title_de":"2 Tage Agadir → Essaouira → Marrakesch", "duration_fr":"2 jours", "duration_en":"2 days", "duration_de":"2 Tage", "price_fr":"180€ / personne", "price_en":"€180 / person", "price_de":"180€ / Person", "details_fr":"", "details_en":"", "details_de":""},
]

@app.before_request
def default_lang():
    session.pop("lang", None)
    if "site_lang" not in session or session.get("site_lang") not in SUPPORTED_LANGS:
        session["site_lang"] = "fr"

def get_lang():
    lang = session.get("site_lang")
    if lang in SUPPORTED_LANGS:
        return lang
    return "fr"

def tr(key):
    lang = get_lang()
    return UI.get(lang, UI["fr"]).get(key, UI["fr"].get(key, key))

@app.context_processor
def inject_tr():
    return {"tr": tr, "current_lang": get_lang()}

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS contact_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                nom TEXT NOT NULL,
                email TEXT NOT NULL,
                telephone TEXT NOT NULL,
                region TEXT,
                date_debut TEXT,
                date_fin TEXT,
                voyageurs INTEGER,
                activites TEXT,
                message TEXT
            )
        """)
        con.commit()

def list_images(abs_folder):
    if not os.path.isdir(abs_folder):
        return []
    files = []
    for fn in os.listdir(abs_folder):
        if os.path.splitext(fn)[1] in IMG_EXT:
            files.append(fn)
    files.sort()
    return files

def get_regions():
    lang = get_lang()
    photos_root = os.path.join(app.static_folder, "photos")
    regions = []
    if not os.path.isdir(photos_root):
        return regions

    for slug in sorted(os.listdir(photos_root)):
        abs_reg = os.path.join(photos_root, slug)
        if not os.path.isdir(abs_reg):
            continue

        imgs = list_images(abs_reg)
        regions.append({
            "slug": slug,
            "name": slug.replace("_", " ").title(),
            "cover": imgs[0] if imgs else None,
            "count": len(imgs),
            "text": REGION_TEXTS.get(lang, REGION_TEXTS["fr"]).get(slug, REGION_TEXTS["fr"].get(slug, "Mini texte à ajouter.")),
            "carousel": []
        })
    return regions

@app.route("/set-lang/<lang_code>", methods=["POST"])
def set_lang(lang_code):
    if lang_code in SUPPORTED_LANGS:
        session["site_lang"] = lang_code
    return redirect(request.referrer or url_for("home"))

@app.route("/", methods=["GET"])
def home():
    regions = get_regions()

    cartes_urls = []
    cartes_root = os.path.join(app.static_folder, "cartes")
    if os.path.isdir(cartes_root):
        for fn in sorted(os.listdir(cartes_root)):
            cartes_urls.append(url_for("static", filename=f"cartes/{fn}"))

    for r in regions:
        abs_reg = os.path.join(app.static_folder, "photos", r["slug"])
        imgs = list_images(abs_reg)[:5]
        r["carousel"] = [url_for("static", filename=f"photos/{r['slug']}/{fn}") for fn in imgs]

    return render_template("home.html", regions=regions, cartes_urls=cartes_urls)

@app.route("/tarifs", methods=["GET"])
def tarifs():
    lang = get_lang()
    grouped = {}
    for t in TARIFS:
        cat = t.get(f"cat_{lang}", t["cat_fr"])
        grouped.setdefault(cat, []).append({
            "titre": t.get(f"title_{lang}", t["title_fr"]),
            "duree": t.get(f"duration_{lang}", t["duration_fr"]),
            "prix": t.get(f"price_{lang}", t["price_fr"]),
            "details": t.get(f"details_{lang}", t["details_fr"]),
        })
    categories = [{"name": k, "rows": grouped[k]} for k in sorted(grouped.keys())]
    return render_template("tarifs.html", categories=categories)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template("contact.html", sent=False)

    init_db()
    nom = (request.form.get("nom") or "").strip()
    email = (request.form.get("email") or "").strip()
    telephone = (request.form.get("telephone") or "").strip()
    region = (request.form.get("region") or "").strip()
    date_debut = (request.form.get("date_debut") or "").strip()
    date_fin = (request.form.get("date_fin") or "").strip()
    voyageurs = request.form.get("voyageurs")
    try:
        voyageurs = int(voyageurs) if voyageurs else None
    except:
        voyageurs = None

    activites = request.form.getlist("activites")
    activites_str = ", ".join([a.strip() for a in activites if a.strip()])
    message = (request.form.get("message") or "").strip()

    if not nom or not email or not telephone:
        return render_template("contact.html", sent=False)

    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """INSERT INTO contact_requests
               (created_at, nom, email, telephone, region, date_debut, date_fin, voyageurs, activites, message)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                datetime.now().isoformat(timespec="seconds"),
                nom, email, telephone, region, date_debut, date_fin,
                voyageurs, activites_str, message
            )
        )
        con.commit()

    return render_template("contact.html", sent=True)

@app.route("/region/<slug>", methods=["GET"])
def region(slug):
    regions = get_regions()
    region_obj = None
    for r in regions:
        if r["slug"] == slug:
            region_obj = r
            break

    if not region_obj:
        abort(404)

    abs_reg = os.path.join(app.static_folder, "photos", slug)
    imgs = list_images(abs_reg)
    photos = [url_for("static", filename=f"photos/{slug}/{fn}") for fn in imgs]

    return render_template("region.html", region=region_obj, photos=photos)

if __name__ == "__main__":
    app.run(debug=True)
