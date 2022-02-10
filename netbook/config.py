from dynaconf import Dynaconf


def load():
    settings = Dynaconf(
        load_dotenv=True,
        settings_files=['settings.toml', '.secrets.toml'],
        merge_enabled=True,
        envvar_prefix="NB",
    )

    return settings
