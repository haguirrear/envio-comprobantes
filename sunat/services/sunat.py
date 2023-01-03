from typing import Any, Optional
import requests
from urllib.parse import urlencode
from envio_comprobantes.exceptions import (
    FailAuthToken,
    FailObteinTicket,
    FailParseTicket,
    FailSendReceipt,
)
from envio_comprobantes.utils import hash_base64_encode_file, zip_single_file
from envio_comprobantes.settings import settings
from pathlib import Path

from pydantic import BaseModel, Field
from rich import print

import logging

logger = logging.getLogger(__name__)


class TicketError(BaseModel):
    num: str = Field(alias="numError")
    detail: str = Field(alias="desError")

    class Config:
        allow_population_by_field_name = True


class TicketResponse(BaseModel):
    response_code: str = Field(alias="codRespuesta")
    error: Optional[TicketError] = Field(None, alias="error")
    receipt_certificate: Optional[str] = Field(None, alias="arcCdr")
    CDR: bool = Field(alias="indCdrGenerado")

    class Config:
        allow_population_by_field_name = True


class SunatService:
    def __init__(
        self, client_id: str, client_secret: str, username: str, password: str
    ) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.auth_token = None

        self.client = requests.Session()

        self.set_auth_token()

    def set_auth_token(self) -> str:
        body = {
            "scope": "https://api-cpe.sunat.gob.pe",
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
        }

        urlencoded_body = urlencode(body)

        url = f"{settings.BASE_AUTH_URL}/v1/clientessol/{self.client_id}/oauth2/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            logger.debug("Obtaining Auth Token")
            response = self.client.post(url=url, data=urlencoded_body, headers=headers)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Fail to get auth token")
            raise FailAuthToken(str(e))

        logger.debug("Auth Token correctly obtained")
        response_json = response.json()
        self.auth_token = response_json["access_token"]

        self.client.headers.update({"Authorization": f"Bearer {self.auth_token}"})

    def send_receipt(self, file_path: Path, zip_folder: Path) -> str:

        filename = file_path.name.split(".")[0]

        zip_path = zip_folder.joinpath(f"{filename}.zip")

        zip_single_file(zip_path=zip_path, filename=str(file_path))

        hash_info = hash_base64_encode_file(zip_path)

        url = f"{settings.BASE_URL}/v1/contribuyente/gem/comprobantes/{filename}"
        hash_info.base64.replace("\n", "")
        payload = {
            "archivo": {
                "nomArchivo": zip_path.name,
                "arcGreZip": hash_info.base64,
                "hashZip": hash_info.hash,
            }
        }
        try:
            response = self.client.post(url=url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Fail to send Receipt")
            raise FailSendReceipt(str(e))

        ticket_num = response.json()["numTicket"]

        return ticket_num

    def get_ticket(self, ticket: str) -> TicketResponse:
        url = f"{settings.BASE_URL}/v1/contribuyente/gem/comprobantes/envios/{ticket}"

        try:
            response = self.client.get(url=url)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Fail to obtain Ticket")
            raise FailObteinTicket(str(e))

        try:
            ticket = TicketResponse.parse_obj(response.json())
        except Exception as e:
            logger.exception("Fail to parse ticket response")
            raise FailParseTicket(response.text) from e

        return ticket
