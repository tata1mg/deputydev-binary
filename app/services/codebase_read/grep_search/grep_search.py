import asyncio
import os
import re
from typing import List
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory

from app.dataclasses.codebase_read.grep_search.grep_search_dataclass import GrepSearchResponse

class GrepSearchService:
    """
    Class to grep files in directory.
    """

    def __init__(self, repo_path: str):
        """
        Initialize the GrepSearch with a directory path.

        :param repo_path: Path to the repository.
        :return: None
        """
        self.repo_path = repo_path

    async def grep(self, directory_path: str, search_terms: list) -> List[GrepSearchResponse]:
        """
        Perform a recursive grep search in the specified directory for multiple terms.

        :param directory_path: Path to the directory to be read.
        :param search_terms: A list of terms to search for in the files.
        :return: A list of GrepSearchResponse objects containing details of each match.
        """
        results = []
        is_git_repo = LocalRepoFactory._is_git_repo(self.repo_path)
        command_template = "grep -rnC 5 '{search_term}' {directory_path}"

        for search_term in search_terms:
            command = command_template.format(search_term=search_term, directory_path=directory_path)
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if stdout:
                output = stdout.decode().strip().splitlines()
                # Use the parser to process the output
                parsed_results = self.parse_lines(output)
                results.extend(parsed_results)

            if stderr:
                print(stderr.decode().strip())

        return results

    def parse_lines(self, input_lines):
        results = []
        for line in input_lines:
            # Use regex to extract the file path and line number
            match = re.search(r'(.+?)(?:-|\:)(\d+)', line)
            if match:
                file_path = match.group(1).strip()
                matched_line = int(match.group(2))  # Convert line number to int

                # Read the file to get all lines first
                try:
                    with open(file_path, 'r') as f:
                        file_lines = f.readlines()

                    total_lines = len(file_lines)
                    matched_line_index = matched_line - 1  # Convert to zero-based index

                    # Calculate start line
                    if matched_line_index < 5:
                        start_line = 0  # If there are fewer than 5 lines above, start from the beginning
                    else:
                        start_line = matched_line_index - 5  # Otherwise, start 5 lines above

                    # Calculate end line
                    if matched_line_index + 5 >= total_lines:
                        end_line = total_lines - 1  # If there are fewer than 5 lines below, end at the last line
                    else:
                        end_line = matched_line_index + 5  # Otherwise, end 5 lines below

                    # Get the content from start_line to end_line
                    content = ''.join(file_lines[start_line:end_line + 1])  # Include end_line in the slice

                    # Create a response object using GrepSearchResponse
                    response = {
                        "file_path": file_path,
                        "start_line": start_line + 1,  # Convert back to one-based index for response
                        "end_line": end_line + 1,  # Convert back to one-based index for response
                        "matched_line": matched_line,
                        "content": content
                    }
                    results.append(response)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

        return results