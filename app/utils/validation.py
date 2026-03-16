import ipaddress
import re


HOSTNAME_REGEX = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*$"
)


def is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_valid_hostname(value: str) -> bool:
    return bool(HOSTNAME_REGEX.match(value))


def is_private_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


def normalize_target(value: str) -> str:
    return value.strip().lower()


def validate_target_format(target: str) -> tuple[bool, str]:
    target = normalize_target(target)

    if is_valid_ip(target):
        return True, target

    if is_valid_hostname(target):
        return True, target

    return False, target