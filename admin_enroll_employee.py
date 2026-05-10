import argparse
import sys

from Utilities.fingerprint_service import (
    DEFAULT_FINGER,
    FingerprintError,
    HelperNotFoundError,
    build_helper_hint,
    enroll_employee,
)


def main():
    parser = argparse.ArgumentParser(
        description="Enroll an employee fingerprint for the Hopkins clock-in/out system."
    )
    parser.add_argument("employee_id", help="Stable employee ID, e.g. EMP001")
    parser.add_argument("name", help="Employee display name")
    parser.add_argument(
        "--finger",
        default=DEFAULT_FINGER,
        help=f"Finger to enroll. Default: {DEFAULT_FINGER}",
    )
    args = parser.parse_args()

    print("Starting fingerprint enrollment.")
    print("The WA28/CS9711 reader may ask for repeated scans before it completes.")

    def print_event(line):
        if line.startswith("DEVICE|"):
            _, name, driver, device_id = line.split("|", 3)
            print(f"Device: {name} ({driver}, {device_id})")
        elif line.startswith("ENROLL_STAGES|"):
            print(f"Enrollment requires {line.split('|', 1)[1]} successful scans.")
        elif line.startswith("PROGRESS|"):
            _, completed, total = line.split("|", 2)
            print(f"Scan accepted: {completed}/{total}")
        elif line.startswith("RETRY|"):
            print(f"Retry: {line.split('|', 1)[1]}")
        elif line.startswith("READY|enroll"):
            print("Place the selected finger on the reader.")

    try:
        employee = enroll_employee(args.employee_id, args.name, args.finger, on_event=print_event)
    except HelperNotFoundError as exc:
        print(str(exc) or build_helper_hint(), file=sys.stderr)
        return 2
    except (ValueError, FingerprintError) as exc:
        print(f"Enrollment failed: {exc}", file=sys.stderr)
        return 1

    print(f"Enrolled {employee.name} ({employee.employee_id}) using {employee.finger}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
