import base64
import zipfile
from pathlib import Path

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


def save_ticket(ticket_response: TicketResponse, output_folder: Path):
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
            print(f"Guardando el ticket en {output_file}")
            zip_tmp.extractall(str(output_folder))

        output_zipfile.unlink()
