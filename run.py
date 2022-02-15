#!/usr/bin/env python3

from netbook.web import create_app

app = create_app()
app.run(
    host=app.config.get("HOST", "127.0.0.1"),
    port=app.config.get("PORT", 5000),
    load_dotenv=False,
)
