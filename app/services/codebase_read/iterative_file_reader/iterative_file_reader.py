from typing import Optional

import aiofiles
from deputydev_core.services.chunking.chunk_info import ChunkInfo, ChunkSourceDetails


class IterativeFileReader:
    """
    Class to read files in an iterative manner.
    """

    def __init__(self, file_path: str, max_lines: Optional[int] = None):
        """
        Initialize the IterativeFileReader with a file path.

        :param file_path: Path to the file to be read.
        :param max_lines: Maximum number of lines to read at once.
        :return: None
        """
        self.file_path = file_path
        self.max_lines: int = max_lines or 100

    async def read_lines(self, start_line: int, end_line: int) -> ChunkInfo:
        """
        Read a chunk of lines from the file starting from the given offset.
        :param start_line: The line number to start reading from.
        :param end_line: The line number to stop reading at.
        :return: A string containing the read lines.

        Reads the file asynchronously in chunks of max_lines.
        """

        if not (end_line) or not (start_line) or not (end_line > start_line):
            raise ValueError("Invalid start_line or end_line")

        async with aiofiles.open(self.file_path, mode="r", encoding="utf-8") as file:
            # Move the file pointer to the start_line
            for line in range(start_line):
                await file.readline()

            file_content: str = ""
            # Read the next min(max_lines, end_line - start_line) lines or until the end of the file

            actual_line_end: Optional[int] = None

            for line_iterator in range(min(self.max_lines, end_line - start_line)):
                line = await file.readline()
                if not line:
                    # End of file reached
                    break
                actual_line_end = start_line + line_iterator
                file_content += line

            if not actual_line_end:
                actual_line_end = start_line + line_iterator

            return ChunkInfo(
                content=file_content,
                embedding=None,
                source_details=ChunkSourceDetails(
                    file_path=self.file_path,
                    start_line=start_line,
                    end_line=actual_line_end,
                ),
            )
