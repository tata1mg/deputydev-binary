from app.models.dtos.code_review_dtos.comment_validity_dto import CommentValidityParams
from app.utils.read_file import read_file_lines
from app.utils.util import hash_content


class CommentValidator:
    LINE_UPDATED = "The line has updated, can not apply comment"
    FILE_DELETED_OR_MOVED = "The file has been moved or deleted."

    async def is_comment_applicable(self, params: CommentValidityParams) -> dict:
        try:
            repo_path, file_path = self.sanitize_path(params.repo_path), self.sanitize_path(params.file_path)
            line, _, _ = await read_file_lines(repo_path + file_path, params.line_number - 1)
            if not line:
                return {"is_applicable": False, "message": self.LINE_UPDATED}

            is_applicable = hash_content(line) == params.line_hash
            msg = "" if is_applicable else self.LINE_UPDATED
            return {"is_applicable": is_applicable, "message": msg}

        except FileNotFoundError:
            return {"is_applicable": False, "message": self.FILE_DELETED_OR_MOVED}

    @staticmethod
    def sanitize_path(path: str) -> str:
        """Sanitize path"""
        return path if path.startswith("/") else f"/{path}"
