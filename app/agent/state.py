from app.storage.schemas import ScanRecord


def add_decision(record: ScanRecord, message: str) -> ScanRecord:
    record.decision_log.append(message)
    return record


def set_step(record: ScanRecord, step: str) -> ScanRecord:
    record.current_step = step
    return record