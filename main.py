from dash import Dash, html, dcc, page_container, page_registry

def create_app() -> Dash:
    app = Dash(
        __name__,
        use_pages=True,
        pages_folder="src/pages",
        suppress_callback_exceptions=True,
        title="Car Crashes Dashboard",
    )

    app.layout = html.Div(
        [
            html.Header(
                [
                    html.H2("Car Crashes Dashboard"),
                    html.Nav(
                        [
                            dcc.Link(page["name"], href=page["path"], style={"marginRight": "12px"})
                            for page in page_registry.values()
                        ]
                    ),
                ],
                style={"padding": "12px 16px", "borderBottom": "1px solid #ddd"},
            ),
            html.Main(page_container, style={"padding": "16px"}),
        ]
    )
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
