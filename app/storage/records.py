from app.storage.schemas import ScanRecord


SCAN_RECORDS: dict[str, ScanRecord] = {}


def save_scan_record(record: ScanRecord) -> ScanRecord:
    SCAN_RECORDS[record.scan_id] = record
    return record


def get_scan_record(scan_id: str) -> ScanRecord | None:
    return SCAN_RECORDS.get(scan_id)