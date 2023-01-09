import base64
import zipfile
from pathlib import Path
from typing import Optional

from rich import print

from sunat_api.services.sunat import SunatService, TicketResponse
from sunat_api.settings import settings


def send(file: Path) -> str:
    """
    Envía un recibo (XML) a SUNAT usando la API REST. El archivo XML debe tener
    el nombre de acuerdo al formato establecido por SUNAT
    """
    service = SunatService(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        password=settings.PASSWORD,
        username=settings.USER,
    )

    ticket = service.send_receipt(
        file_path=file,
    )
    return ticket


def get(
    ticket: str,
) -> TicketResponse:
    service = SunatService(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        password=settings.PASSWORD,
        username=settings.USER,
    )

    ticket_response = service.get_ticket(ticket)

    return ticket_response


def save_ticket(
    ticket_response: TicketResponse,
    output_folder: Path,
    xml_name: Optional[str] = None,
    error_folder: Optional[Path] = None,
):
    if ticket_response.receipt_certificate:
        output_zipfile = output_folder.joinpath("temp.zip")
        with output_zipfile.open("wb") as tmp:
            decoded_data = base64.decodebytes(
                ticket_response.receipt_certificate.encode("ASCII")
            )
            tmp.write(decoded_data)
            tmp.seek(0)

        with zipfile.ZipFile(str(output_zipfile), "r") as zip_tmp:
            output_file = output_folder.joinpath(zip_tmp.filelist[0].filename)
            print(f"[bold green]Guardando el ticket en {output_file}[/bold green]")
            zip_tmp.extractall(str(output_folder))

        output_zipfile.unlink()
    else:
        print(
            "[bold yellow]No se recibió ningun archivo del API de SUNAT[/bold yellow]"
        )

    if ticket_response.is_error:
        if error_folder is not None:
            error_file_name = xml_name.split(".")[0] + "_error.txt"
            error_file_path = error_folder.joinpath(error_file_name)
            print(f"[bold green]Guardando error en: {error_file_path}[/bold green]")
            error_file_path.write_text(
                f"Error Code: {ticket_response.error.num} | Detail: {ticket_response.error.detail}"
            )
        else:
            print(
                "[bold red]No se especifico una carpeta donde guardar el error[/bold red]"
            )
