from typing import Dict

from deputydev_core.services.repo.local_repo.dataclasses.main import DiffTypes
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory
from deputydev_core.utils.app_logger import AppLogger


class DiffApplicatorService:
    def apply_diff(
            self,
            repo_path: str,
            file_path_to_diff_map: Dict[str, str],
            diff_type: DiffTypes = DiffTypes.UDIFF,
    ) -> Dict[str, str]:
        try:
            self.clean_pathces(file_path_to_diff_map)
            repo = LocalRepoFactory.get_local_repo(repo_path)
            return repo.get_modified_file_content(
                diff=file_path_to_diff_map, diff_type=diff_type
            )
        except Exception as _ex:
            AppLogger.log_error(f"Error while applying diff: {_ex}")
            return {}

    def clean_pathces(self, file_path_to_diff_map: dict) -> None:
        for file_path, patch in file_path_to_diff_map.items():
            # Keep everything from the first '---' onward
            start_index = patch.find('---')
            if start_index == -1:
                return ""

            # Remove everything from the last '```' (inclusive)
            end_index = patch.rfind('```')
            if end_index != -1:
                text = patch[start_index:end_index]
            else:
                text = patch[start_index:]
            file_path_to_diff_map[file_path] = text.strip()
