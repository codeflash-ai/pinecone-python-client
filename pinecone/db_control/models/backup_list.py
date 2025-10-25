import json
from pinecone.core.openapi.db_control.model.backup_list import BackupList as OpenAPIBackupList
from .backup_model import BackupModel
from typing import List


class BackupList:
    def __init__(self, backup_list: OpenAPIBackupList):
        self._backup_list = backup_list
        # Use a local variable to avoid repeated attribute access
        backups_data = backup_list.data
        # Preallocate the list size if backups_data supports __len__
        if hasattr(backups_data, "__len__"):
            backups_len = len(backups_data)
            self._backups = [None] * backups_len
            for i, b in enumerate(backups_data):
                self._backups[i] = BackupModel(b)
        else:
            self._backups = [BackupModel(b) for b in backups_data]

    def names(self) -> List[str]:
        return [i.name for i in self._backups]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._backups[key]
        elif key == "data":
            return self._backups
        else:
            # pagination and any other keys added in the future
            return self._backup_list[key]

    def __getattr__(self, attr):
        # Avoid repeated string comparison by using direct boolean check
        if attr == "data":
            return self._backups
        # Directly return the attribute from the underlying object
        return getattr(self._backup_list, attr)

    def __len__(self):
        return len(self._backups)

    def __iter__(self):
        return iter(self._backups)

    def __str__(self):
        return str(self._backups)

    def __repr__(self):
        raw_dict = self._backup_list.to_dict()
        raw_dict["data"] = [i.to_dict() for i in self._backups]

        # Remove keys with value None
        for key, value in list(raw_dict.items()):
            if value is None:
                del raw_dict[key]

        return json.dumps(raw_dict, indent=4)
