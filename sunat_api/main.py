import logging
from typing import Optional
from pathlib import Path
import typer
from sunat_api.services.sunat import SunatService
from sunat_api.settings import settings
from rich import print
from sunat_api.subcommands import config
from sunat_api.subcommands import recibo
from sunat_api.utils import base64_to_file

logging.basicConfig(level=settings.LOG_LEVEL)

if settings.LOG_LEVEL == "DEBUG":
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


app = typer.Typer()
app.add_typer(
    config.app,
    name="config",
    help="Ver o modificar las configuraciones y credenciales",
)
app.add_typer(
    recibo.app,
    name="recibo",
    help="Enviar y obtener Recibos de SUNAT",
)


@app.callback()
def main(
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


if __name__ == "__main__":
    app()
