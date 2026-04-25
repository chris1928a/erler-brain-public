"""Google Drive API — search files."""
import os
import json
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

logger = logging.getLogger("gdrive")


def _get_drive_service():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")
    creds_data = json.loads(creds_json)
    creds = Credentials(
        token=None,
        refresh_token=creds_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=["https://www.googleapis.com/auth/drive.readonly"],
    )
    return build("drive", "v3", credentials=creds)


async def search_drive(query: str, max_results: int = 10) -> list:
    """Search Google Drive for files matching query."""
    service = _get_drive_service()
    results = service.files().list(
        q=f"fullText contains '{query}' and trashed = false",
        pageSize=max_results,
        fields="files(id, name, mimeType, modifiedTime, webViewLink)",
        orderBy="modifiedTime desc",
    ).execute()

    return [
        {
            "name": f.get("name"),
            "type": f.get("mimeType", "").split(".")[-1],
            "modified": f.get("modifiedTime", "")[:10],
            "link": f.get("webViewLink", ""),
        }
        for f in results.get("files", [])
    ]
