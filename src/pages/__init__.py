import dash
from dash import html

dash.register_page(__name__, path="/", name="Accueil")

layout = html.Div("Hello")
