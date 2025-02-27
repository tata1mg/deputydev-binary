from typing import Dict
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory
from deputydev_core.services.repo.local_repo.dataclasses.main import DiffTypes


class DiffApplicatorService:
    def apply_diff(
        self,
        repo_path: str,
        file_path_to_diff_map: Dict[str, str],
        diff_type: DiffTypes = DiffTypes.UDIFF,
    ):
        repo = LocalRepoFactory.get_local_repo(repo_path)
        repo.apply_diff(file_path_to_diff_map, diff_type)
