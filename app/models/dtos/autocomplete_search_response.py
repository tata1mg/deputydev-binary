from typing import Dict, List, Optional

from pydantic import BaseModel


class ChunkRange(BaseModel):
    start_line: int
    end_line: int


class CodeSymbol(BaseModel):
    type: str
    value: Optional[str] = None
    file_path: str
    chunks: List[ChunkRange]
    score: float

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "value": self.value,
            "path": self.file_path,
            "chunks": [
                {"start_line": c.start_line, "end_line": c.end_line}
                for c in self.chunks
            ],
        }
