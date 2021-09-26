from typing import Dict, List, Union

from pydantic import BaseModel


class LocalMemeSchema(BaseModel):
    type: str
    chat_id: int
    data: Union[Dict, List]
