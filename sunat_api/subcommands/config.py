from typing import Optional
import typer
from rich import print
from sunat_api.settings import settings

app = typer.Typer()


@app.command()
def show():
    """
    Mostrar las configuraciones y credenciales del programa
    """
    print(settings.dict())


@app.command()
def set(
    user: Optional[str] = typer.Option(
        None,
        "--user",
        "-u",
        help="Usuario (RUC+Usuario SOL)",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Clave SOL",
    ),
    client_id: Optional[str] = typer.Option(
        None,
        help="Client Id para el uso de la API de SUNAT",
    ),
    client_secret: Optional[str] = typer.Option(
        None,
        help="Client Secret para el uso de la API de SUNAT",
    ),
    base_auth_url: Optional[str] = typer.Option(
        None, help="URL base para el endpoint de obtener Token"
    ),
    base_url: Optional[str] = typer.Option(
        None, help="URL base para las apis de SUNAT"
    ),
    log_level: Optional[str] = typer.Option(None, help="Log level"),
):
    """
    Modificar las configuraciones y credenciales del programa
    """
    if user is not None:
        settings.USER = user
    if password is not None:
        settings.PASSWORD = password
    if client_id is not None:
        settings.CLIENT_ID = client_id
    if client_secret is not None:
        settings.CLIENT_SECRET = client_secret
    if base_auth_url is not None:
        settings.BASE_AUTH_URL = base_auth_url
    if base_url is not None:
        settings.BASE_URL = base_url
    if log_level is not None:
        settings.LOG_LEVEL = log_level

    new_settings = settings.json()

    settings.CONFIG_PATH.write_text(
        new_settings, encoding=settings.__config__.env_file_encoding
    )
    print("Se actualizó correctamente los settings")
