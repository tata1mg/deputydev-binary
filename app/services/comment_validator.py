from app.utils.read_file import read_file_lines
from app.models.dtos.code_review_dtos.comment_validity_dto import CommentValidityParams
from app.utils.util import hash_content


class CommentValidator:
    LINE_UPDATED = "The line has updated, can not apply comment"
    FILE_DELETED_OR_MOVED = "The file has been moved or deleted."

    async def is_comment_applicable(self, params: CommentValidityParams) -> dict:
        try:
            line, _, _ = await read_file_lines(params.repo_path + params.file_path, params.line_number - 1)
            if not line:
                return {"is_applicable": False, "message": self.LINE_UPDATED}

            is_applicable = hash_content(line) == params.line_hash
            msg = "" if is_applicable else self.LINE_UPDATED
            return {"is_applicable": is_applicable, "message": msg}

        except FileNotFoundError:
            return {"is_applicable": False, "message": self.FILE_DELETED_OR_MOVED}