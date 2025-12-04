"""License placeholder for fully open OSS build (all features allowed)."""


class LicenseManager:
    """Trivial manager: everything is always permitted."""

    def check_feature(self, feature: str) -> bool:  # noqa: ARG002
        return True

    def require_pro(self, feature: str):  # noqa: ARG002
        return


license_manager = LicenseManager()
