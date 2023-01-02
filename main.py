import logging
from typing import Optional
from pathlib import Path
import typer
from envio_comprobantes.services.sunat import SunatService
from envio_comprobantes.settings import settings
from rich import print

from envio_comprobantes.utils import base64_to_file

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
    file: Path = typer.Argument(..., exists=True, file_okay=True),
    zip_folder: Path = typer.Argument(Path.cwd(), exists=True, dir_okay=True),
    user: str = typer.Option(
        ..., "--user", "-u", prompt="Por favor intruduce el usuario"
    ),
    password: str = typer.Option(
        ..., "--password", "-p", prompt="Por favor intruduce la clave SOL"
    ),
):

    service = SunatService(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        password=password,
        username=user,
    )

    ticket = service.send_receipt(
        file_path=file,
        zip_folder=zip_folder,
    )

    print("Recibo enviado correctamente!")
    print(f"Se genero el ticket: [bold green]{ticket}[/bold green]")


@app.command()
def obtener_recibo(
    ticket: str,
    output_folder: Optional[Path] = typer.Option(
        Path.cwd(), exists=True, dir_okay=True
    ),
    user: str = typer.Option(
        ..., "--user", "-u", prompt="Por favor intruduce el usuario"
    ),
    password: str = typer.Option(
        ..., "--password", "-p", prompt="Por favor intruduce la clave SOL"
    ),
):
    service = SunatService(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
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
        output_file = output_folder.joinpath(ticket)
        print(f"Guardando el ticket en {output_file}")
        base64_to_file(
            base64_string=ticket_response.receipt_certificate,
            filepath=output_file,
        )


if __name__ == "__main__":
    app()
