import time
from pathlib import Path
from typing import Optional

import typer
from rich import print

from sunat_api import constants
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
    output_folder: Path = typer.Option(
        Path.cwd(),
        "--output-folder",
        "-o",
        exists=True,
        dir_okay=True,
        help="Carpeta donde guardar el ticket de SUNAT. Si no es proporcionada se guardara en la carpeta actual",
    ),
):
    """
    Obtiene un ticket previamente enviado a SUNAT usando la API REST. Se debe proporcionar
    un ticket.
    """

    ticket_response = recibo.get(ticket)
    recibo.save_ticket(ticket_response, output_folder)

    if ticket_response.response_code == constants.TICKET_ERROR_RESPONSE_CODE:
        print(
            f"[bold red]Hubo un error al obtener el ticket:[/bold red] {ticket_response}"
        )
        typer.Exit(code=1)
    elif ticket_response.response_code == constants.TICKET_SUCCESS_RESPONSE_CODE:
        print(f"Se obtuvo el ticket: {ticket_response}")
    elif ticket_response.response_code == constants.TICKET_PROCESING_RESPONSE_CODE:
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
        help="Carpeta donde guardar el ticket de SUNAT. Si no es proporcionada se guardara en la carpeta actual",
    ),
    error_folder: Optional[Path] = typer.Option(
        None,
        "--error-folder",
        "-e",
        exists=True,
        dir_okay=True,
        help="Carpeta donde guardar el mensaje de error si es que existe",
    ),
):
    """
    Envia un recibo y luego obtiene el ticket usando el API REST de SUNAT
    (Simplificacion de los comandos "enviar" y "obtener")
    """
    ticket = recibo.send(file)
    print("[bold green]Recibo enviado correctamente![/bold green]")
    print(f"Se generó el ticket: [bold green]{ticket}[/bold green]")

    time.sleep(1)
    ticket_response = recibo.get(ticket)

    if ticket_response.is_processing:
        print("El ticket se encuentra en proceso...")

        count = 0
        while ticket_response.is_processing and count < 10:
            count += 1
            time.sleep(2)
            ticket_response = recibo.get(ticket)

        if ticket_response.is_processing:
            print(
                f"El recibo sigue en proceso: {ticket_response}. Puede consultarlo nuevo con este numero de ticket: {ticket}"
            )

    if ticket_response.is_error:
        print(
            f"[bold red]Hubo un error al obtener el ticket:\n{ticket_response.error.num}: {ticket_response.error.detail}[/bold red]"
        )
    elif ticket_response.is_success:
        print(f"Recibo obtenido con exito:\n{ticket}")

    recibo.save_ticket(
        ticket_response,
        output_folder,
        xml_name=file.name,
        error_folder=error_folder,
    )
