from dataclasses import dataclass


@dataclass(frozen=True)
class DataQualityResult:
    transaction_date: str | None
    validated_count: int
    failed_checks: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return not self.failed_checks