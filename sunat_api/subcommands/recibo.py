import time
from typing import Optional
from pathlib import Path
import typer
from sunat_api.services.sunat import SunatService
from sunat_api.settings import settings
from rich import print
from sunat_api.subcommands import config
from sunat_api.utils import base64_to_file
import typer

from sunat_api.services import recibo

app = typer.Typer()


@app.command()
def enviar(
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        help="Ruta al archivo xml que se quiere enviar a SUNAT",
    ),
):
    """
    Envía un recibo (XML) a SUNAT usando la API REST. El archivo XML debe tener
    el nombre de acuerdo al formato establecido por SUNAT
    """
    ticket = recibo.send(file)
    print("Recibo enviado correctamente!")
    print(f"Se genero el ticket: [bold green]{ticket}[/bold green]")


@app.command()
def obtener(
    ticket: str = typer.Argument(
        ..., help="Número de Ticket obtenido al enviar el recibo a SUNAT"
    ),
    output_folder: Optional[Path] = typer.Option(
        Path.cwd(),
        "--output-folder",
        "-o",
        exists=True,
        dir_okay=True,
        help="Carpeta dodne guardar el ticket de SUNAT. Si no es proporcionada se guardara en la carpeta actual",
    ),
):
    """
    Obtiene un ticket previamente enviado a SUNAT usando la API REST. Se debe proporcionar
    un ticket.
    """

    ticket_response = recibo.get(ticket)
    recibo.save_ticket(ticket, ticket_response, output_folder)

    if ticket_response.response_code == "99":
        print(
            f"[bold red]Hubo un error al obtener el ticket:[/bold red] {ticket_response}"
        )
        typer.Exit(code=1)
    elif ticket_response.response_code == "0":
        print(f"Se obtuvo el ticket: {ticket_response}")
    elif ticket_response.response_code == "98":
        print(f"El ticket se encuentra en proceso: {ticket_response}")


@app.command()
def enviar_obtener(
    file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        help="Ruta al archivo xml que se quiere enviar a SUNAT",
    ),
    output_folder: Optional[Path] = typer.Option(
        Path.cwd(),
        "--output-folder",
        "-o",
        exists=True,
        dir_okay=True,
        help="Carpeta dodne guardar el ticket de SUNAT. Si no es proporcionada se guardara en la carpeta actual",
    ),
):
    """
    Envia un recibo y luego obtiene el ticket usando el API REST de SUNAT
    (Simplificacion de los comandos "enviar" y "obtener")
    """
    ticket = recibo.send(file)

    print(f"Se obtuvo el ticket: [bold red]{ticket}[\bold red]")

    ticket_response = recibo.get(ticket)

    if ticket_response.response_code == "99":
        print(
            f"[bold red]Hubo un error al obtener el ticket:[/bold red] {ticket_response}"
        )
        typer.Exit(code=1)
    elif ticket_response.response_code == "0":
        recibo.save_ticket(ticket, ticket_response, output_folder)
    elif ticket_response.response_code == "98":
        print(f"El ticket se encuentra en proceso: {ticket_response}")

        time.sleep(2)
        count = 0
        while ticket_response.response_code == "98" and count < 10:
            time.sleep(2)
            ticket_response = recibo.get(ticket)
            count += 1

        if ticket_response.response_code == "98":
            print(
                f"El recibo sigue en proceso: {ticket_response}. Puede consultarlo nuevo con este numero de ticket: {ticket}"
            )
