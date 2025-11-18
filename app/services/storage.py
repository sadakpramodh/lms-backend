"""Local disk storage stub."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from fastapi import UploadFile

from ..config import get_settings
from ..schemas import DisputeFileMetadata


def save_files(user_id: str, files: Iterable[UploadFile]) -> List[DisputeFileMetadata]:
    settings = get_settings()
    bucket = Path(settings.storage_bucket)
    bucket.mkdir(parents=True, exist_ok=True)

    saved: List[DisputeFileMetadata] = []
    for file in files:
        user_dir = bucket / user_id
        user_dir.mkdir(exist_ok=True)
        target_path = user_dir / file.filename
        content = file.file.read()
        target_path.write_bytes(content)
        saved.append(
            DisputeFileMetadata(
                filename=file.filename,
                url=f"/storage/{user_id}/{file.filename}",
                size_bytes=len(content),
            )
        )
    return saved
