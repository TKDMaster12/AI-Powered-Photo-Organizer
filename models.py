from pydantic import BaseModel
from typing import List, Optional

class PhotoMetadata(BaseModel):
    suggested_folder: str # e.g., "Pets", "Travel", "Receipts"
    tags: List[str]
    quality_score: int    # 1-10 (How blurry or well-composed is it?)
    is_clutter: bool      # True if it's a screenshot or accidental pocket-photo
    description: str      # A brief caption of what's in the photo