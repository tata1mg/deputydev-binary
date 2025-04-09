import asyncio
import re
from typing import Any, Dict, List
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory

from app.dataclasses.codebase_search.grep_search.grep_search_dataclass import GrepSearchResponse

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
        if is_git_repo:
            command_template = "git --git-dir={repo_path}/.git --work-tree={repo_path} grep -rnC 5 '{search_term}' -- {directory_path}"
        else:
            command_template = "grep -rnC 5 '{search_term}' {directory_path} {exclude_flags}"

        exclude_dirs = [
            "node_modules", "dist", "build", ".venv", ".git", "out", "venv",
            "__pycache__", "target", "bin", "obj", "vendor", "log", "tmp", "packages"
        ]
        exclude_flags = " ".join(f"--exclude-dir={d}" for d in exclude_dirs)

        for search_term in search_terms:
            command = command_template.format(
                search_term=search_term,
                directory_path=directory_path,
                repo_path=self.repo_path,
                exclude_flags=exclude_flags
            )
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if stdout:
                parsed_results = self.parse_lines(stdout.decode().strip().splitlines(), is_git_repo)
                results.extend(parsed_results)

            if stderr:
                print(stderr.decode().strip())

        return results[:100]

    def parse_lines(self, input_lines, is_git_repo: bool) -> list[Dict[str, Any]]:
        results = []
        chunk_lines = []

        def process_chunk(chunk):
            if not chunk:
                return None

            # Step 4: Find the exact match line (with `:` after line number)
            match_line = None
            file_path = None
            start_line = None
            end_line = None
            code_lines = []

            for line in chunk:
                match = re.match(r"^(.*?):(\d+):(.*)$", line)
                if match:
                    file_path = match.group(1).strip()
                    match_line = int(match.group(2))
                    code_lines.append(match.group(3).strip())
                    break

            if not file_path or match_line is None:
                return None

            # Step 2: Get all line numbers in the chunk (even context lines)
            line_numbers = []
            for line in chunk:
                match_context = re.match(rf"^{re.escape(file_path)}[-:](\d+)[-:]?(.*)$", line)
                if match_context:
                    line_num = int(match_context.group(1))
                    line_numbers.append(line_num)

            if not line_numbers:
                return None

            start_line = min(line_numbers)
            end_line = max(line_numbers)

            # Step 5 & 6: Remove file path and line numbers from all lines to get clean code
            for line in chunk:
                clean = re.sub(rf"^{re.escape(file_path)}[-:](\d+)[-:]?", "", line).strip()
                code_lines.append(clean)

            # Step 7: Join into a clean block of code
            chunk_text = "\n".join(code_lines)
            if not is_git_repo:
                file_path = file_path.replace(self.repo_path, "")
            return {
                "file_path": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "match_line": match_line,
                "content": chunk_text
            }

        # Step 1: Split into chunks using '--'
        for line in input_lines:
            if line.strip() == "--":
                result = process_chunk(chunk_lines)
                if result:
                    results.append(result)
                chunk_lines = []
            else:
                chunk_lines.append(line)

        # Final chunk flush
        if chunk_lines:
            result = process_chunk(chunk_lines)
            if result:
                results.append(result)

        return results