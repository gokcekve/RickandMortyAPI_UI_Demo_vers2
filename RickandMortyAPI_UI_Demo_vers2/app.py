from flask import Flask, render_template, request
import requests
import math

app = Flask(__name__)

BASE_URL = "https://rickandmortyapi.com/api/character"

def fetch_all_characters(params):
    # API'den filtreli ya da filtresiz tüm verileri çeken fonksyon

    all_characters = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            characters = data.get("results", [])
            all_characters.extend(characters)
            # Daha fazla sayfa varsa devam et
            if "info" in data and data["info"].get("next"):
                page += 1
            else:
                break
        else:
            break

    return all_characters

# GET apiden gelen veriyi almak için;
# POST apiye karakter detaylarını talpe etmek için
@app.route("/", methods=["GET", "POST"])
def index():
    # Form POST edilirse
    character_details = None
    """
    # Daha öncekden girilmiş aktif filtre olamdığından emin olalım:
    filters = {"name": None, "status": None, "species": None, "gender": None}

    # Filtreleme işlemi
    if request.method == "POST":
        char_id = request.form.get("char_id")
        if char_id:
            # Karakter detaylarını almak için API'ye istek at
            response = requests.get(f"{BASE_URL}/{char_id}")
            if response.status_code == 200:
                character_details = response.json()
        else:
            filters["name"] = request.form.get("name")
            filters["status"] = request.form.get("status")
            filters["species"] = request.form.get("species")
            filters["gender"] = request.form.get("gender")
    """
    # Parametreleri al
    name = request.args.get("name", "")
    status = request.args.get("status", "")
    species = request.args.get("species", "")
    gender = request.args.get("gender", "")
    sort_by = request.args.get("sort_by", "")
    sort_order = request.args.get("sort_order", "asc")
    page = request.args.get("page", 1, type=int)
    rows_per_page = request.args.get("rows_per_page", 250, type=int)
    # Her sayfada default oalrak 250 satır yer alır ancak kullanıcı bu sayıyı değiştirebilir

    # API'den filtrelenmiş tüm verileri çek
    params = {"name": name, "status": status, "species": species, "gender": gender}
    filtered_characters = fetch_all_characters(params)  # Sadece filtrelenmiş veriler döner

    # Eğer filtrelere uygun veri yoksa uyarı mesajı göster
    no_data_message = ""
    if not filtered_characters:
        no_data_message = "No data available for the filters!"

    # Filtrelenmiş veriler üzerinde sıralama yap
    if sort_by:
        filtered_characters = sorted(
            filtered_characters,
            key=lambda x: x.get(sort_by, "").lower() if isinstance(x.get(sort_by), str) else x.get(sort_by),
            reverse=(sort_order == "desc"),
        )

    # Toplam sonuç sayısını ve toplam sayfa sayısını hesapla
    total_results = len(filtered_characters)
    total_pages = math.ceil(total_results / rows_per_page)
    # Sayfalama için verileri böl
    start_index = (page - 1) * rows_per_page
    end_index = start_index + rows_per_page
    paginated_characters = filtered_characters[start_index:end_index]

    # Karakter detaylarını al : test kodu (yerini değiştir)
    character_details = None
    if request.method == "POST":
        char_id = request.form.get("char_id")
        # Karakterin detaylarını API'den çek
        response = requests.get(f"{BASE_URL}/{char_id}")
        if response.status_code == 200:
            character_details = response.json()

    return render_template(
        "index.html",
        characters=paginated_characters,
        total_pages=total_pages,
        current_page=page,
        rows_per_page=rows_per_page,
        filters={"name": name, "status": status, "species": species, "gender": gender},
        sort_by=sort_by,
        sort_order=sort_order,
        no_data_message=no_data_message,  # Mesajı şablona gönder
        character_details=character_details,  # Detayları gönder
    )

if __name__ == "__main__":
    app.run(debug=True)