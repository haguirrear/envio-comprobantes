import logging
from typing import Optional
from pathlib import Path
import typer
from sunat_api.services.sunat import SunatService
from sunat_api.settings import settings
from rich import print

from sunat_api.utils import base64_to_file

logging.basicConfig(level=settings.LOG_LEVEL)

if settings.LOG_LEVEL == "DEBUG":
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


app = typer.Typer()


@app.command()
def enviar_recibo(
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        help="Ruta al archivo xml que se quiere enviar a SUNAT",
    ),
    user: str = typer.Option(
        ...,
        "--user",
        "-u",
        prompt="Por favor intruduce el usuario",
        help="Usuario (RUC+Usuario SOL)",
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        prompt="Por favor intruduce la clave SOL",
        help="Clave SOL",
    ),
    client_id: str = typer.Option(
        ...,
        prompt="Por favor introduce el client_id a usar",
        help="Client Id para el uso de la API de SUNAT",
    ),
    client_secret: str = typer.Option(
        ...,
        prompt="Por favor introduce el client_secret a usar",
        help="Client Secret para el uso de la API de SUNAT",
    ),
):
    """
    Envía un recibo (XML) a SUNAT usando la API REST. El archivo XML debe tener
    el nombre de acuerdo al formato establecido por SUNAT
    """
    service = SunatService(
        client_id=client_id,
        client_secret=client_secret,
        password=password,
        username=user,
    )

    ticket = service.send_receipt(
        file_path=file,
    )

    print("Recibo enviado correctamente!")
    print(f"Se genero el ticket: [bold green]{ticket}[/bold green]")


@app.command()
def obtener_recibo(
    ticket: str = typer.Argument(
        ..., help="Número de Ticket obtenido al enviar el recibo a SUNAT"
    ),
    output_folder: Optional[Path] = typer.Option(
        Path.cwd(),
        exists=True,
        dir_okay=True,
        help="Carpeta dodne guardar el ticket de SUNAT. Si no es proporcionada se guardara en la carpeta actual",
    ),
    user: str = typer.Option(
        ...,
        "--user",
        "-u",
        prompt="Por favor intruduce el usuario",
        help="Usuario (RUC+Usuario SOL)",
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-p",
        prompt="Por favor intruduce la clave SOL",
        help="Clave SOL",
    ),
    client_id: str = typer.Option(
        ...,
        prompt="Por favor introduce el client_id a usar",
        help="Client Id para el uso de la API de SUNAT",
    ),
    client_secret: str = typer.Option(
        ...,
        prompt="Por favor introduce el client_secret a usar",
        help="Client Secret para el uso de la API de SUNAT",
    ),
):
    """
    Obtiene un ticket previamente enviado a SUNAT usando la API REST. Se debe proporcionar
    un ticket.
    """
    service = SunatService(
        client_id=client_id,
        client_secret=client_secret,
        password=password,
        username=user,
    )

    ticket_response = service.get_ticket(ticket)

    if ticket_response.response_code == "99":
        print(
            f"[bold red]Hubo un error al obtener el ticket:[/bold red] {ticket_response}"
        )
        typer.Exit(code=1)
    elif ticket_response.response_code == "0":
        print(f"Se obtuvo el ticket: {ticket_response}")
    elif ticket_response.response_code == "98":
        print(f"El ticket se encuentra en proceso: {ticket_response}")

    if ticket_response.receipt_certificate:
        output_file = output_folder.joinpath(f"{ticket}.zip")
        print(f"Guardando el ticket en {output_file}")
        base64_to_file(
            base64_string=ticket_response.receipt_certificate,
            filepath=output_file,
        )


if __name__ == "__main__":
    app()
