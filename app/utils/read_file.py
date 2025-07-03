from typing import Tuple
import aiofiles


async def read_file_lines(file_path, start_line: int, lines_to_read: int = 1) -> Tuple[str, int, bool]:
    """
    Reads the file line-by-line starting from `start_line`, reading up to `lines_to_read` lines.
    Returns:
        - The content read as a string.
        - The actual end line reached.
        - A boolean indicating if EOF was hit before reading all requested lines.
    """
    file_content = ""
    current_line_num = 0
    eof_reached = False

    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as file:
            for _ in range(start_line - 1):
                if not await file.readline():
                    return "", start_line, True

            for i in range(lines_to_read):
                line = await file.readline()
                if not line:
                    eof_reached = True
                    break
                file_content += line
                current_line_num = start_line + i

        return file_content, current_line_num or start_line, eof_reached

    except FileNotFoundError:
        raise
