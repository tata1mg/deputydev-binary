from typing import Optional
import aiofiles


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

    async def read_lines(self, offset_line: Optional[int] = None) -> str:
        """
        Read a chunk of lines from the file starting from the given offset.
        :param offset: The starting point for reading lines.
        :return: A string containing the read lines.

        Reads the file asynchronously in chunks of max_lines.
        """
        offset_to_use = offset_line or 0

        async with aiofiles.open(self.file_path, mode="r", encoding="utf-8") as file:
            # Move to the offset line
            for line in range(offset_to_use):
                await file.readline()

            file_content: str = ""
            # Read the next max_lines lines
            for _ in range(self.max_lines):
                line = await file.readline()
                if not line:
                    break
                file_content += line
            return file_content
