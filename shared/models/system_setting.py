class SystemSetting:

    def __init__(
        self,
        setting_id: int = None,
        setting_key: str = None,
        setting_value: str = None,
        updated_at: str = None,
    ):
        self.setting_id = setting_id
        self.setting_key = setting_key
        self.setting_value = setting_value
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return (
            f"SystemSetting(id={self.setting_id}, "
            f"key='{self.setting_key}')"
        )