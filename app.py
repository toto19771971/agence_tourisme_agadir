from flask import Flask, render_template, abort, url_for, request, redirect, session
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "tourisme_fr"

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".JPG", ".JPEG", ".PNG", ".WEBP", ".GIF"}
DB_PATH = os.path.join(os.path.dirname(__file__), "bookings.db")

SUPPORTED_LANGS = ["fr", "en", "de"]

UI = {'fr': {'nav_home': 'Accueil', 'nav_contact': 'Contact / Réservation', 'nav_tarifs': 'Nos tarifs', 'cta_contact': 'Contact / Réservation', 'cta_tarifs': 'Nos tarifs', 'home_title': 'Nos 11 régions en images', 'home_intro_title': 'Bienvenue au Sud du Maroc', 'home_intro_text': """Bienvenue dans le Souss, au Sud du Maroc : un territoire où l’océan Atlantique rencontre les montagnes de l’Anti‑Atlas, des vallées vertes, et les premières portes du désert.

Depuis Agadir, vous pouvez tout faire sans courir : respirer l’air marin au petit matin, prendre une route panoramique l’après‑midi, puis savourer une cuisine simple et généreuse le soir — poissons grillés, tajines, amlou, miel, huile d’argan… Ici, chaque sortie change d’ambiance : surf et plages à Taghazout, piscines naturelles à la Vallée du Paradis, villages amazighs et roches roses vers Tafraout, argent et artisanat à Tiznit, falaises rouges et arches sur la côte de Legzira, dunes au bord de l’océan à Timlalin, fraîcheur et cascades du côté d’Imouzzer.

Notre promesse : des excursions bien organisées, un rythme agréable, des lieux photogéniques, et surtout une expérience humaine. Vous ne “consommez” pas une activité : vous vivez un Sud marocain authentique — paysages, histoire, rencontres, et souvenirs.

Choisissez une région ci‑dessous : chaque carte ouvre une atmosphère différente. Et si vous hésitez, contactez‑nous : nous vous conseillons selon votre temps, votre budget et vos envies.
""", 'home_feat_1_t': 'Excursions', 'home_feat_1_s': 'Des sorties organisées, confortables et simples.', 'home_feat_2_t': 'Découverte', 'home_feat_2_s': 'Océan, montagnes, villages, oasis, désert : tout proche.', 'home_feat_3_t': 'Souvenirs', 'home_feat_3_s': 'Photos, paysages, rencontres : une journée qui reste.', 'home_map_title': 'Carte de la région', 'home_map_sub': 'Repérez nos points de départ et nos zones d’excursion.', 'region_about': 'À propos de cette région', 'region_photos': 'Photos', 'reserve': 'Contact / Réservation', 'back': 'Retour', 'contact_title': 'Contact / Réservation', 'contact_sub': 'Dites-nous ce que vous souhaitez faire, nous vous répondons rapidement.', 'f_name': 'Nom', 'f_email': 'Email', 'f_phone': 'Téléphone', 'f_region': 'Région', 'f_date_from': 'Date (du)', 'f_date_to': 'Date (au)', 'f_people': 'Nombre de personnes', 'f_activities': 'Activités souhaitées', 'f_message': 'Message', 'f_message_ph': 'Décrivez ce que vous souhaitez faire (durée, niveau, préférences)', 'send': 'Envoyer', 'sent_ok': 'Message envoyé', 'sent_ok_sub': 'Merci. Nous vous recontactons rapidement.', 'payment': 'Paiement', 'payment_note': 'Paiement en ligne disponible bientôt. Vous pouvez déjà réserver par message.', 'pay_paypal': 'Paiement PayPal (bientôt)', 'tarifs_title': 'Nos tarifs', 'tarifs_sub': 'Prix indicatifs. Contactez-nous pour un devis selon votre groupe et la saison.', 't_exp': 'Expérience', 't_duree': 'Durée', 't_prix': 'Prix', 't_details': 'Détails', 'footer_contact': 'Adresse : Nehda Lkobra double voie · Téléphone : +41 79 558 15 41 · E‑mail : robot.comptable@gmail.com · WhatsApp : +41 79 558 15 41'}, 'en': {'nav_home': 'Home', 'nav_contact': 'Contact / Booking', 'nav_tarifs': 'Prices', 'cta_contact': 'Contact / Booking', 'cta_tarifs': 'Prices', 'home_title': 'Our 11 regions in pictures', 'home_intro_title': 'Welcome to Southern Morocco', 'home_intro_text': """Welcome to the Souss, in Southern Morocco: a land where the Atlantic Ocean meets the Anti‑Atlas mountains, green valleys, and the first gateways to the desert.

From Agadir, you can explore without rushing: ocean air in the morning, scenic roads in the afternoon, and generous local food in the evening — grilled fish, tagines, amlou, honey, argan oil… Each outing brings a different mood: surf beaches in Taghazout, natural pools in Paradise Valley, Amazigh villages and pink granite around Tafraout, silver craft and heritage in Tiznit, red cliffs and coastal arches near Legzira, ocean‑side dunes at Timlalin, and fresh mountain scenery around Immouzzar.

Our promise: well‑organized trips, a comfortable pace, photogenic spots, and above all a warm human experience. You don’t just “book an activity” — you live an authentic Southern Morocco: landscapes, history, encounters, and lasting memories.

Pick a region below: each card opens a new atmosphere. And if you are not sure, contact us — we will recommend the best plan for your time, budget, and interests.
""", 'home_feat_1_t': 'Trips', 'home_feat_1_s': 'Well organized, comfortable, and easy.', 'home_feat_2_t': 'Discover', 'home_feat_2_s': 'Ocean, mountains, villages, oases, desert — all nearby.', 'home_feat_3_t': 'Memories', 'home_feat_3_s': 'Photos, landscapes, encounters — a day you remember.', 'home_map_title': 'Regional map', 'home_map_sub': 'Find our departure points and excursion areas.', 'region_about': 'About this region', 'region_photos': 'Photos', 'reserve': 'Contact / Booking', 'back': 'Back', 'contact_title': 'Contact / Booking', 'contact_sub': 'Tell us what you would like to do — we reply quickly.', 'f_name': 'Name', 'f_email': 'Email', 'f_phone': 'Phone', 'f_region': 'Region', 'f_date_from': 'Date (from)', 'f_date_to': 'Date (to)', 'f_people': 'People', 'f_activities': 'Activities', 'f_message': 'Message', 'f_message_ph': 'Describe what you would like to do (duration, level, preferences)', 'send': 'Send', 'sent_ok': 'Message sent', 'sent_ok_sub': 'Thank you. We will contact you shortly.', 'payment': 'Payment', 'payment_note': 'Online payment coming soon. You can already book by message.', 'pay_paypal': 'PayPal payment (soon)', 'tarifs_title': 'Prices', 'tarifs_sub': 'Indicative prices. Contact us for a quote depending on group size and season.', 't_exp': 'Experience', 't_duree': 'Duration', 't_prix': 'Price', 't_details': 'Details', 'footer_contact': 'Address: Nehda Lkobra double voie · Phone: +41 79 558 15 41 · Email: robot.comptable@gmail.com · WhatsApp: +41 79 558 15 41'}, 'de': {'nav_home': 'Startseite', 'nav_contact': 'Kontakt / Reservierung', 'nav_tarifs': 'Preise', 'cta_contact': 'Kontakt / Reservierung', 'cta_tarifs': 'Preise', 'home_title': 'Unsere 11 Regionen in Bildern', 'home_intro_title': 'Willkommen im Süden Marokkos', 'home_intro_text': """Willkommen im Souss, im Süden Marokkos: eine Region, in der der Atlantik auf das Anti‑Atlas‑Gebirge trifft, wo grüne Täler, Oasen und die ersten Tore zur Wüste beginnen.

Von Agadir aus können Sie entspannt entdecken: Meeresluft am Morgen, Panoramastraßen am Nachmittag und abends eine ehrliche, großzügige Küche — gegrillter Fisch, Tajine, Amlou, Honig, Arganöl… Jede Ausfahrt hat eine andere Stimmung: Surfstrände in Taghazout, Naturbecken im Paradise Valley, Amazigh‑Dörfer und rosafarbener Granit rund um Tafraout, Silberhandwerk und Traditionen in Tiznit, rote Klippen und Küstenbögen bei Legzira, Dünen direkt am Ozean in Timlalin sowie frische Berglandschaften in der Gegend von Immouzzar.

Unser Versprechen: gut organisierte Ausflüge, ein angenehmes Tempo, sehr fotogene Orte und vor allem ein menschliches Erlebnis. Sie „buchen“ nicht einfach eine Aktivität — Sie erleben den authentischen Süden Marokkos: Landschaften, Geschichte, Begegnungen und Erinnerungen.

Wählen Sie unten eine Region: Jede Karte öffnet eine neue Atmosphäre. Und wenn Sie unsicher sind, kontaktieren Sie uns — wir empfehlen Ihnen gerne die beste Route je nach Zeit, Budget und Ihren Wünschen.
""", 'home_feat_1_t': 'Ausflüge', 'home_feat_1_s': 'Gut organisiert, bequem und unkompliziert.', 'home_feat_2_t': 'Entdecken', 'home_feat_2_s': 'Ozean, Berge, Dörfer, Oasen, Wüste — alles in der Nähe.', 'home_feat_3_t': 'Erinnerungen', 'home_feat_3_s': 'Fotos, Landschaften, Begegnungen — ein Tag, der bleibt.', 'home_map_title': 'Regionalkarte', 'home_map_sub': 'Finden Sie unsere Startpunkte und Ausflugsgebiete.', 'region_about': 'Über diese Region', 'region_photos': 'Fotos', 'reserve': 'Kontakt / Reservierung', 'back': 'Zurück', 'contact_title': 'Kontakt / Reservierung', 'contact_sub': 'Sagen Sie uns, was Sie machen möchten — wir antworten schnell.', 'f_name': 'Name', 'f_email': 'E‑Mail', 'f_phone': 'Telefon', 'f_region': 'Region', 'f_date_from': 'Datum (von)', 'f_date_to': 'Datum (bis)', 'f_people': 'Personen', 'f_activities': 'Aktivitäten', 'f_message': 'Nachricht', 'f_message_ph': 'Beschreiben Sie, was Sie machen möchten (Dauer, Niveau, Wünsche)', 'send': 'Senden', 'sent_ok': 'Nachricht gesendet', 'sent_ok_sub': 'Vielen Dank. Wir melden uns schnell.', 'payment': 'Zahlung', 'payment_note': 'Online‑Zahlung kommt bald. Sie können bereits per Nachricht reservieren.', 'pay_paypal': 'PayPal‑Zahlung (bald)', 'tarifs_title': 'Preise', 'tarifs_sub': 'Unverbindliche Preise. Kontaktieren Sie uns für ein Angebot je nach Gruppe und Saison.', 't_exp': 'Erlebnis', 't_duree': 'Dauer', 't_prix': 'Preis', 't_details': 'Details', 'footer_contact': 'Adresse: Nehda Lkobra double voie · Telefon: +41 79 558 15 41 · E‑Mail: robot.comptable@gmail.com · WhatsApp: +41 79 558 15 41'}}

REGION_TEXTS = {'fr': {'agadir': """Agadir est la porte d’entrée idéale pour découvrir le Sud : une grande baie lumineuse, une promenade en bord de mer, et une ville tournée vers l’Atlantique. Depuis la Kasbah (Oufella), la vue embrasse le port, la plage et les montagnes au loin. La ville porte aussi une histoire forte : après le séisme de 1960, elle a été reconstruite et modernisée.

Agadir est surtout une base parfaite pour rayonner : marchés, produits du terroir (argan, miel, amlou), cuisine de la mer, et excursions faciles vers Taghazout, la Vallée du Paradis, Imouzzer, Taroudant, Tiznit, Tafraout ou les dunes côtières. Que vous aimiez la détente, la photo, la nature ou la culture, tout est à portée de route.

Si vous souhaitez une journée “zéro stress”, c’est ici que l’organisation devient simple : prise en charge, itinéraires optimisés, pauses bien placées, et un rythme agréable pour profiter pleinement.
""", 'taghazout_village_colore': """Taghazout est un village de pêcheurs devenu un spot de surf réputé, tout en gardant une ambiance décontractée. Entre cafés face à l’océan, ruelles simples et points de vue sur la côte, l’endroit est idéal pour respirer et ralentir.

Selon la saison, vous pouvez observer les surfeurs, faire une balade au coucher du soleil, ou explorer les petites plages et criques voisines. L’atmosphère est “bord de mer”, mais avec ce petit côté bohème qui fait le charme de la côte sud.

C’est une sortie parfaite si vous voulez mélanger mer, photo, et détente, sans faire de longs trajets.
""", 'vallee_paradis': """La Vallée du Paradis est une oasis au pied des montagnes, connue pour ses bassins naturels, ses palmiers et ses gorges rocheuses. On y vient pour marcher tranquillement, respirer l’air frais, et profiter d’un décor très différent d’Agadir en moins d’une heure de route.

Sur place, vous pouvez suivre un sentier accessible, faire des pauses près de l’eau, et, selon la météo et le niveau des bassins, vous baigner dans les “piscines naturelles”. Le contraste est saisissant : roches, verdure, eau claire, et vues sur l’Atlas.

Conseil : en excursion, tout devient plus simple (route, timing, meilleurs points). L’objectif est de profiter sans se presser : nature, photo, et détente.
""", 'cascade_immouzzar': """Imouzzer et ses environs offrent une parenthèse de fraîcheur dans l’arrière‑pays : routes de montagne, petites vallées, et un décor plus “vert” selon la saison. Historiquement, la zone est connue pour ses paysages et pour la fameuse “route du miel”, appréciée pour les produits locaux.

Selon la période de l’année, vous pourrez voir des points d’eau et des zones plus humides, faire des pauses dans des cafés de montagne, et découvrir des villages où le rythme est très différent de la côte. C’est une sortie agréable si vous cherchez l’air frais et un Maroc plus rural.

L’intérêt est autant dans la balade panoramique que dans l’arrivée : l’arrière‑pays du Souss réserve souvent de belles surprises.
""", 'tafraout': """Tafraout, au cœur de l’Anti‑Atlas, est célèbre pour ses montagnes de granit rose, ses formations rocheuses et ses villages amazighs. La lumière y est particulière : au lever et au coucher du soleil, les reliefs prennent des teintes chaudes incroyables, parfaites pour la photo.

La région se découvre par étapes : points de vue, petits villages, palmeraies, et vallées comme celle des Ammeln. On peut aussi aller vers des gorges et des oasis cachées, où la verdure surgit au milieu des roches.

Si vous aimez les paysages “carte postale” et une ambiance plus authentique, Tafraout est un incontournable du Sud.
""", 'tiznit': """Tiznit est une ville au charme traditionnel, connue pour ses remparts et son artisanat, notamment l’orfèvrerie et le travail de l’argent. Flâner dans la médina et ses souks, c’est entrer dans un Maroc plus calme, plus local, où l’on prend le temps.

C’est aussi un excellent point pour comprendre la culture du Souss : habitudes, produits, artisanat, et architecture. On y trouve des places animées, des ateliers, et des coins parfaits pour acheter un souvenir de qualité.

En excursion, Tiznit se combine facilement avec la côte (Mirleft/Legzira) ou l’intérieur, selon vos envies.
""", 'arches_igzira': """La côte de Legzira (près de Sidi Ifni / Mirleft) est célèbre pour ses falaises rouges et ses arches naturelles sculptées par l’océan. L’endroit est spectaculaire, surtout quand la lumière descend : le rouge des roches devient profond et le contraste avec l’Atlantique est magnifique.

La visite dépend beaucoup des marées : à marée basse, vous pouvez marcher plus loin sur le sable et approcher les formations rocheuses. C’est une sortie très “photo” et très “nature”, avec une sensation de grands espaces.

Si vous aimez l’océan sauvage et les paysages uniques, Legzira est une étape qui marque.
""", 'timlaline': """Timlalin est connue pour ses dunes au bord de l’océan : un paysage rare où le sable rencontre l’Atlantique. Le lieu est parfait pour une balade simple, des photos, et une pause au calme loin de l’agitation.

Selon l’heure, les dunes prennent des couleurs dorées et les ombres dessinent des lignes magnifiques. On peut marcher sur les crêtes, regarder le coucher du soleil, ou simplement profiter du vent et du bruit des vagues.

C’est une sortie courte, facile, et très “waouh”, idéale si vous voulez un décor différent sans aller loin.
""", 'petit_desert': """Le “petit désert” (selon l’itinéraire) offre une première expérience des paysages arides du Sud : plaines ouvertes, reliefs secs, couleurs minérales, et parfois quelques dunes. C’est l’endroit parfait pour ressentir l’ambiance du désert sans faire un très long trajet.

On y vient pour les panoramas, les photos, et cette impression d’espace. Avec un bon timing, la lumière transforme le décor et rend chaque arrêt spectaculaire.

Si vous voulez une journée dépaysante, simple et très visuelle, c’est une excellente option.
""", 'essaouira': """Essaouira, plus au nord sur la côte Atlantique, est une ville de caractère : remparts, médina classée, ruelles blanches et bleues, et un port très vivant. L’ambiance y est différente d’Agadir : plus historique, plus artistique, avec une brise quasi permanente.

On peut y passer la journée entre balade sur les remparts, découverte de la médina, dégustation de poisson au port, et shopping d’artisanat (bois de thuya, produits locaux). C’est aussi un paradis pour la photo.

Essaouira plaît autant aux amoureux d’histoire qu’aux voyageurs qui aiment flâner, manger et se laisser porter.
""", 'marrakech': """Marrakech est une immersion totale : la médina, ses souks, ses palais, ses jardins et l’énergie unique de la place Jemaa el‑Fna. C’est une ville intense, colorée, où chaque ruelle raconte une histoire.

Selon votre rythme, vous pouvez visiter des incontournables (jardins, palais, musées), puis vous perdre dans les souks pour sentir l’ambiance et découvrir l’artisanat. La cuisine et les rooftops au coucher du soleil font aussi partie de l’expérience.

C’est une grande journée, mais si vous voulez voir “l’icône” du Maroc, Marrakech reste une étape inoubliable.
"""}, 'en': {'agadir': """Agadir is the perfect gateway to Southern Morocco: a bright bay, long seaside promenades, and a city shaped by the Atlantic. From the Kasbah hill (Oufella), you can see the harbor, the beach, and the mountains in the distance. Agadir also carries a powerful story — after the 1960 earthquake, the city was rebuilt and modernized.

It is above all a great base for day trips: local markets, regional products (argan oil, honey, amlou), seafood, and easy routes to Taghazout, Paradise Valley, Immouzzar, Tiznit, Tafraout, coastal dunes, and more. Whether you prefer relaxation, photography, nature, or culture, everything is within reach.

If you want a “no‑stress” day, this is where good organization makes the difference: smooth pick‑up, smart routes, well‑timed stops, and a comfortable pace.
""", 'taghazout_village_colore': """Taghazout is a fishing village that became a famous surf spot while keeping its relaxed vibe. Oceanfront cafés, simple streets, and coastal viewpoints make it a perfect place to slow down.

Depending on the season, you can watch surfers, walk at sunset, or explore nearby coves and beaches. The atmosphere is pure seaside — with a small bohemian touch that gives the coast its charm.

It’s an ideal half‑day or day trip if you want to combine ocean views, photos, and easy relaxation.
""", 'vallee_paradis': """Paradise Valley is an oasis in the foothills, known for its palm trees, rocky gorges, and natural pools. People come to walk, breathe fresh air, and enjoy a completely different scenery from Agadir — in less than an hour by road.

On site, you can follow an easy trail, stop near the water, and, depending on conditions, swim in the natural pools. The contrast is striking: stone, greenery, clear water, and mountain views.

With a guided plan, everything becomes smoother (road, timing, best viewpoints). The goal is simple: enjoy nature, photos, and calm moments without rushing.
""", 'cascade_immouzzar': """Immouzzar and its surroundings offer a refreshing break inland: mountain roads, small valleys, and greener scenery depending on the season. The area is also known for local products and the famous “honey route” of the region.

According to the time of year, you may see water spots and cooler corners, stop in small mountain cafés, and discover villages where life feels far from the coastal rhythm. It’s a great option if you want fresh air and a more rural side of Morocco.

The beauty is as much in the panoramic drive as in the destination — the Souss backcountry often surprises visitors.
""", 'tafraout': """Tafraout, in the heart of the Anti‑Atlas, is famous for its pink granite mountains, rock formations, and Amazigh villages. The light here is special: at sunrise and sunset, the landscape turns warm and dramatic — perfect for photography.

You discover the area step by step: viewpoints, small villages, palm groves, and valleys such as the Ammeln Valley. Nearby, hidden gorges and oasis pockets reveal greenery in the middle of the rocks.

If you love postcard landscapes and a more authentic atmosphere, Tafraout is a must in Southern Morocco.
""", 'tiznit': """Tiznit is a traditional town known for its ramparts and craftsmanship, especially silver jewelry and artisanal work. Walking through the medina and its souks feels calmer and more local — a place where people take their time.

It is also a great way to understand Souss culture: daily life, products, crafts, and architecture. You’ll find lively squares, workshops, and excellent spots to buy a quality souvenir.

Tiznit can easily be combined with the coast (Mirleft/Legzira) or the inland routes, depending on your interests.
""", 'arches_igzira': """Legzira’s coastline (near Sidi Ifni / Mirleft) is famous for its red cliffs and natural sea arches shaped by the Atlantic. The scenery is dramatic, especially late in the day when the red rock becomes deeper and contrasts beautifully with the ocean.

The visit depends on the tide: at low tide you can walk farther on the sand and get closer to the rock formations. It’s a very “nature + photography” outing with a strong feeling of open space.

If you enjoy wild ocean landscapes and unique geology, Legzira is a stop you will remember.
""", 'timlaline': """Timlalin is known for its dunes right next to the ocean — a rare landscape where sand meets the Atlantic. It’s perfect for an easy walk, beautiful photos, and a quiet break away from crowds.

At the right time, the dunes turn golden and the shadows draw clean lines across the sand. You can walk along the ridges, watch the sunset, or simply enjoy the wind and the sound of waves.

It’s short, easy, and genuinely impressive — ideal if you want a different scenery without going far.
""", 'petit_desert': """The “small desert” (depending on the route) offers a first taste of Southern Morocco’s arid landscapes: open plains, mineral colors, dry reliefs, and sometimes a few dunes. It’s a great way to feel the desert atmosphere without a very long drive.

People come for wide panoramas, strong photos, and the sense of space. With good timing, the light transforms the scenery and makes every stop look cinematic.

If you want a simple, visual, and change‑of‑scene day, it’s an excellent option.
""", 'essaouira': """Essaouira, farther north on the Atlantic coast, is a city with character: ramparts, a historic medina, white‑and‑blue streets, and a very lively harbor. The atmosphere is different from Agadir — more historic and artistic, with a constant ocean breeze.

You can spend the day walking the walls, exploring the medina, tasting fresh fish at the port, and shopping local crafts (thuya wood, regional products). It’s also a great place for photography.

Essaouira works for travelers who love history, food, and relaxed wandering.
""", 'marrakech': """Marrakech is a full immersion: the medina, souks, palaces, gardens, and the unique energy of Jemaa el‑Fna square. It’s intense, colorful, and unforgettable.

Depending on your pace, you can visit key landmarks (gardens, palaces, museums) and then get lost in the souks to feel the city’s heartbeat and discover craftsmanship. Rooftops at sunset and Moroccan cuisine are part of the experience.

It’s a big day trip, but if you want to see Morocco’s iconic city, Marrakech is a classic you will never forget.
"""}, 'de': {'agadir': """Agadir ist der ideale Ausgangspunkt für den Süden: eine helle Bucht, lange Promenaden und eine Stadt im Rhythmus des Atlantiks. Von der Kasbah‑Anh Höhe (Oufella) sehen Sie Hafen, Strand und die Berge in der Ferne. Agadir hat auch eine starke Geschichte — nach dem Erdbeben von 1960 wurde die Stadt neu aufgebaut und modernisiert.

Vor allem ist Agadir eine perfekte Basis für Tagesausflüge: Märkte, regionale Produkte (Arganöl, Honig, Amlou), frischer Fisch und einfache Routen nach Taghazout, Paradise Valley, Immouzzar, Tiznit, Tafraout, zu den Küstendünen und mehr. Ob Entspannung, Fotografie, Natur oder Kultur — vieles ist schnell erreichbar.

Wenn Sie einen „stressfreien“ Tag wünschen, macht eine gute Organisation den Unterschied: Abholung, sinnvolle Route, richtige Stopps und ein angenehmes Tempo.
""", 'taghazout_village_colore': """Taghazout ist ein Fischerdorf, das zum bekannten Surfspot wurde und dabei seine entspannte Atmosphäre behalten hat. Cafés mit Meerblick, einfache Gassen und Küstenpanoramen machen es ideal, um langsamer zu werden.

Je nach Saison können Sie Surfer beobachten, bei Sonnenuntergang spazieren gehen oder kleine Buchten und Strände in der Nähe entdecken. Das Gefühl ist „Meer“ — mit einem leichten, bohemischen Touch.

Perfekt für einen halben oder ganzen Tag, wenn Sie Ozean, Fotos und entspannte Zeit kombinieren möchten.
""", 'vallee_paradis': """Das Paradise Valley ist eine Oase am Fuß der Berge, bekannt für Palmen, Felsenschluchten und Naturbecken. Man kommt zum Spazieren, um frische Luft zu atmen und eine Landschaft zu sehen, die sich stark von Agadir unterscheidet — in weniger als einer Stunde Fahrt.

Vor Ort folgen Sie einem einfachen Weg, machen Pausen am Wasser und können je nach Bedingungen in den natürlichen Pools baden. Der Kontrast ist beeindruckend: Fels, Grün, klares Wasser und Bergblicke.

Mit guter Planung läuft alles ruhiger (Straße, Timing, beste Aussichtspunkte). Ziel ist: Natur, Fotos und Entspannung ohne Hektik.
""", 'cascade_immouzzar': """Immouzzar und die Umgebung bieten eine frische Auszeit im Hinterland: Bergstraßen, kleine Täler und je nach Saison deutlich grünere Landschaften. Die Gegend ist außerdem für lokale Produkte bekannt, besonders für die „Honigroute“.

Je nach Jahreszeit sehen Sie kühlere Ecken und Wasserstellen, können in kleinen Bergcafés pausieren und Dörfer entdecken, in denen das Leben ganz anders als an der Küste wirkt. Ideal, wenn Sie frische Luft und ein ländlicheres Marokko möchten.

Der Reiz liegt sowohl in der Panoramafahrt als auch im Ziel — das Hinterland des Souss überrascht oft.
""", 'tafraout': """Tafraout im Anti‑Atlas ist berühmt für rosafarbenen Granit, besondere Felsformen und Amazigh‑Dörfer. Das Licht ist einzigartig: Bei Sonnenauf‑ und ‑untergang wirken die Berge warm und dramatisch — perfekt für Fotos.

Sie entdecken die Region Schritt für Schritt: Aussichtspunkte, kleine Dörfer, Palmenhaine und Täler wie das Ammeln‑Tal. In der Nähe zeigen Schluchten und versteckte Oasen plötzlich Grün mitten im Fels.

Wenn Sie Postkartenlandschaften und eine authentische Atmosphäre lieben, ist Tafraout ein Muss.
""", 'tiznit': """Tiznit ist eine traditionelle Stadt, bekannt für ihre Stadtmauern und ihr Handwerk — vor allem Silberschmuck und Kunsthandwerk. Ein Spaziergang durch die Medina und die Souks wirkt ruhiger und lokaler: Hier nimmt man sich Zeit.

Gleichzeitig ist es ein guter Ort, um die Kultur des Souss zu verstehen: Alltag, Produkte, Handwerk und Architektur. Sie finden Plätze, Werkstätten und sehr schöne Möglichkeiten für hochwertige Souvenirs.

Tiznit lässt sich gut mit der Küste (Mirleft/Legzira) oder einer Route ins Inland kombinieren.
""", 'arches_igzira': """Die Küste von Legzira (bei Sidi Ifni / Mirleft) ist berühmt für rote Klippen und natürliche Meeresbögen, die vom Atlantik geformt wurden. Die Szenerie ist spektakulär, besonders am späten Nachmittag, wenn das Rot der Felsen tiefer wird.

Der Besuch hängt von den Gezeiten ab: Bei Ebbe können Sie weiter am Strand entlanggehen und näher an die Felsformationen kommen. Es ist ein perfekter Ausflug für Natur und Fotografie, mit viel Weite.

Wenn Sie wilde Ozeanlandschaften und besondere Geologie mögen, bleibt Legzira in Erinnerung.
""", 'timlaline': """Timlalin ist bekannt für Dünen direkt am Ozean — ein seltenes Bild, bei dem Sand und Atlantik aufeinandertreffen. Ideal für einen einfachen Spaziergang, schöne Fotos und eine ruhige Pause abseits des Trubels.

Zur richtigen Zeit werden die Dünen golden, und die Schatten zeichnen klare Linien in den Sand. Sie können über die Kämme laufen, den Sonnenuntergang ansehen oder einfach Wind und Wellen genießen.

Kurz, leicht und wirklich beeindruckend — perfekt, wenn Sie ohne lange Fahrt etwas Besonderes sehen möchten.
""", 'petit_desert': """Die „kleine Wüste“ (je nach Route) bietet einen ersten Eindruck der trockenen Landschaften des Südens: weite Ebenen, mineralische Farben, aride Reliefs und manchmal einige Dünen. Sie erleben die Wüstenstimmung, ohne sehr weit fahren zu müssen.

Man kommt wegen der Panoramen, der starken Fotos und des Gefühls von Raum. Mit gutem Timing verwandelt das Licht die Szenerie und macht jeden Halt spektakulär.

Wenn Sie einen einfachen, visuellen Tapetenwechsel suchen, ist das eine sehr gute Option.
""", 'essaouira': """Essaouira an der Atlantikküste ist eine Stadt mit Charakter: Stadtmauern, eine historische Medina, weiß‑blaue Gassen und ein sehr lebendiger Hafen. Die Atmosphäre ist anders als in Agadir — historischer und künstlerischer, mit fast ständigem Wind.

Sie können den Tag mit einem Spaziergang auf den Mauern, einem Bummel durch die Medina, frischem Fisch am Hafen und Handwerk (Thuya‑Holz, regionale Produkte) füllen. Auch fotografisch ist es ein Traum.

Essaouira passt für alle, die Geschichte, Essen und entspanntes Flanieren mögen.
""", 'marrakech': """Marrakesch ist ein intensives Erlebnis: Medina, Souks, Paläste, Gärten und die einzigartige Energie des Platzes Jemaa el‑Fna. Es ist farbig, lebendig und unvergesslich.

Je nach Tempo besuchen Sie wichtige Orte (Gärten, Paläste, Museen) und tauchen dann in die Souks ein, um die Stimmung zu spüren und Handwerk zu entdecken. Rooftops zum Sonnenuntergang und marokkanische Küche gehören dazu.

Es ist ein großer Tagesausflug, aber wenn Sie Marokkos ikonische Stadt sehen möchten, ist Marrakesch ein Klassiker.
"""}}

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
