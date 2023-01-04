from pathlib import Path

from sunat_api.services.sunat import SunatService, TicketResponse
from sunat_api.settings import settings
from sunat_api.utils import base64_to_file


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


def save_ticket(ticket: str, ticket_response: TicketResponse, output_folder: Path):
    if ticket_response.receipt_certificate:
        output_file = output_folder.joinpath(f"{ticket}.zip")
        print(f"Guardando el ticket en {output_file}")
        base64_to_file(
            base64_string=ticket_response.receipt_certificate,
            filepath=output_file,
        )
