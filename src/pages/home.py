from pathlib import Path
from src.utils.lumin_histo import generate_luminosite_histogram

def generate_homepage():
    img_path = generate_luminosite_histogram(2005, 2024)

    img_rel = Path(img_path).as_posix()

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dashboard Accidents</title>
    </head>
    <body>
        <h1>Dashboard des accidents</h1>

        <h2>Histogramme de la luminosité</h2>
        <img src="{img_rel}" alt="Histogramme luminosité" style="max-width:600px;">

    </body>
    </html>
    """

    out_file = Path("homepage.html")
    out_file.write_text(html, encoding="utf-8")

    print(f"[OK] Homepage générée → {out_file.absolute()}")
    print("Ouvre-la dans ton navigateur (double-clique).")

if __name__ == "__main__":
    generate_homepage()
