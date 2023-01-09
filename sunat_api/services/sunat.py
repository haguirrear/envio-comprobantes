import logging
import tempfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

import requests
from pydantic import BaseModel, Field

from sunat_api import constants
from sunat_api.exceptions import (
    FailAuthToken,
    FailObteinTicket,
    FailParseTicket,
    FailSendReceipt,
)
from sunat_api.settings import settings
from sunat_api.utils import hash_base64_encode_file, zip_single_file

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
    CDR: Optional[bool] = Field(None, alias="indCdrGenerado")

    @property
    def is_success(self) -> bool:
        return self.response_code == constants.TICKET_SUCCESS_RESPONSE_CODE

    @property
    def is_error(self) -> bool:
        return self.response_code == constants.TICKET_ERROR_RESPONSE_CODE

    @property
    def is_processing(self) -> bool:
        return self.response_code == constants.TICKET_PROCESING_RESPONSE_CODE

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

    def send_receipt(self, file_path: Path, write_zip: bool = False) -> str:

        logger.debug("File to be zipped: %s", str(file_path))

        filename = file_path.name.split(".")[0]
        logger.debug("Just filename: %s", filename)

        zip_filename = f"{filename}.zip"

        bytes_info = None
        with tempfile.SpooledTemporaryFile() as tmp:
            zip_single_file(zip_handle=tmp, filename=str(file_path))
            tmp.seek(0)
            hash_info = hash_base64_encode_file(tmp)
            tmp.seek(0)
            bytes_info = tmp.read()

        if write_zip:
            with open(file_path.parent.joinpath(zip_filename), "wb") as zip_2:
                zip_2.write(bytes_info)

        url = f"{settings.BASE_URL}/v1/contribuyente/gem/comprobantes/{filename}"
        hash_info.base64.replace("\n", "")
        payload = {
            "archivo": {
                "nomArchivo": zip_filename,
                "arcGreZip": hash_info.base64,
                "hashZip": hash_info.hash,
            }
        }
        try:
            response = self.client.post(url=url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Fail to send Receipt")
            if getattr(e, "response") is not None:
                logger.exception("Response Body: %s", e.response.text)
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
            if getattr(e, "response") is not None:
                logger.exception("Response Body: %s", e.response.text)
            raise FailObteinTicket(str(e))

        try:
            ticket = TicketResponse.parse_obj(response.json())
        except Exception as e:
            logger.exception("Fail to parse ticket response")
            raise FailParseTicket(response.text) from e

        return ticket
