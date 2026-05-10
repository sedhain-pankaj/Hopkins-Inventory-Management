import csv
import os
import re
import selectors
import shutil
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path

from Utilities.constants import (
    BASE_DIR,
    DATA_DIR,
    EMPLOYEE_REGISTRY_FILEPATH,
    FINGERPRINT_HELPER_ENV,
    FINGERPRINT_STORAGE_DIR,
    TIME_CLOCK_LOG_FILEPATH,
)


EMPLOYEE_HEADERS = ["employee_id", "name", "finger", "enrolled_at", "active"]
TIME_LOG_HEADERS = ["timestamp", "employee_id", "employee_name", "action", "source"]
EMPLOYEE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
DEFAULT_FINGER = "right-index"


class FingerprintError(Exception):
    pass


class HelperNotFoundError(FingerprintError):
    pass


class NoMatchError(FingerprintError):
    pass


@dataclass
class Employee:
    employee_id: str
    name: str
    finger: str = DEFAULT_FINGER
    enrolled_at: str = ""
    active: bool = True


@dataclass
class ClockEvent:
    timestamp: str
    employee_id: str
    employee_name: str
    action: str
    source: str = "fingerprint"


def ensure_data_files():
    Path(DATA_DIR).mkdir(mode=0o700, parents=True, exist_ok=True)
    Path(FINGERPRINT_STORAGE_DIR).mkdir(mode=0o700, parents=True, exist_ok=True)
    _chmod_quiet(DATA_DIR, 0o700)
    _chmod_quiet(FINGERPRINT_STORAGE_DIR, 0o700)

    if not os.path.exists(EMPLOYEE_REGISTRY_FILEPATH):
        _write_csv_headers(EMPLOYEE_REGISTRY_FILEPATH, EMPLOYEE_HEADERS)
    if not os.path.exists(TIME_CLOCK_LOG_FILEPATH):
        _write_csv_headers(TIME_CLOCK_LOG_FILEPATH, TIME_LOG_HEADERS)


def build_helper_hint():
    return (
        "Build the CS9711 helper first:\n"
        "  meson setup libfprint-CS9711/build libfprint-CS9711 "
        "-Ddrivers=cs9711 -Ddoc=false -Dgtk-examples=false "
        "-Dintrospection=false -Dinstalled-tests=false "
        "-Dudev_rules=disabled -Dudev_hwdb=disabled\n"
        "  ninja -C libfprint-CS9711/build examples/employee-clock-helper\n\n"
        f"Or point {FINGERPRINT_HELPER_ENV} at a built employee-clock-helper binary."
    )


def sanitize_employee_id(employee_id):
    employee_id = (employee_id or "").strip()
    if not employee_id:
        raise ValueError("Employee ID is required.")
    if not EMPLOYEE_ID_PATTERN.fullmatch(employee_id):
        raise ValueError("Employee ID may only contain letters, numbers, dot, dash, and underscore.")
    return employee_id


def load_employees(include_inactive=False):
    ensure_data_files()
    employees = []
    with open(EMPLOYEE_REGISTRY_FILEPATH, newline="", encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            active = row.get("active", "1").strip().lower() not in {"0", "false", "no"}
            if active or include_inactive:
                employees.append(
                    Employee(
                        employee_id=row.get("employee_id", "").strip(),
                        name=row.get("name", "").strip(),
                        finger=row.get("finger", DEFAULT_FINGER).strip() or DEFAULT_FINGER,
                        enrolled_at=row.get("enrolled_at", "").strip(),
                        active=active,
                    )
                )
    return [employee for employee in employees if employee.employee_id]


def get_employee(employee_id, include_inactive=False):
    employee_id = sanitize_employee_id(employee_id)
    for employee in load_employees(include_inactive=include_inactive):
        if employee.employee_id == employee_id:
            return employee
    return None


def upsert_employee(employee):
    ensure_data_files()
    rows = []
    found = False
    with open(EMPLOYEE_REGISTRY_FILEPATH, newline="", encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            if row.get("employee_id") == employee.employee_id:
                rows.append(_employee_to_row(employee))
                found = True
            else:
                rows.append(row)
    if not found:
        rows.append(_employee_to_row(employee))
    _write_csv_rows(EMPLOYEE_REGISTRY_FILEPATH, EMPLOYEE_HEADERS, rows)


def find_helper_binary():
    configured = os.environ.get(FINGERPRINT_HELPER_ENV)
    if configured and os.path.exists(configured) and os.access(configured, os.X_OK):
        return configured

    candidates = [
        os.path.join(BASE_DIR, "libfprint-CS9711", "build", "examples", "employee-clock-helper"),
        os.path.join(BASE_DIR, "libfprint-CS9711", "builddir", "examples", "employee-clock-helper"),
        os.path.join(BASE_DIR, "libfprint-CS9711", "_build", "examples", "employee-clock-helper"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate

    path_binary = shutil.which("employee-clock-helper")
    if path_binary:
        return path_binary

    return None


def enroll_employee(employee_id, name, finger=DEFAULT_FINGER, on_event=None, timeout=360):
    employee_id = sanitize_employee_id(employee_id)
    name = (name or "").strip()
    if not name:
        raise ValueError("Employee name is required.")
    finger = (finger or DEFAULT_FINGER).strip()

    lines = _run_helper(["enroll", FINGERPRINT_STORAGE_DIR, employee_id, finger], timeout, on_event)
    if not any(line.startswith("ENROLLED|") for line in lines):
        raise FingerprintError("Enrollment did not complete successfully.")

    employee = Employee(
        employee_id=employee_id,
        name=name,
        finger=finger,
        enrolled_at=datetime.now().isoformat(timespec="seconds"),
        active=True,
    )
    upsert_employee(employee)
    secure_fingerprint_files()
    return employee


def identify_employee(on_event=None, timeout=120):
    employees = {employee.employee_id: employee for employee in load_employees()}
    if not employees:
        raise FingerprintError("No enrolled employees were found.")

    lines = _run_helper(["identify", FINGERPRINT_STORAGE_DIR], timeout, on_event)
    for line in lines:
        if line.startswith("MATCH|"):
            employee_id = line.split("|", 1)[1].strip()
            employee = employees.get(employee_id) or get_employee(employee_id, include_inactive=True)
            if not employee:
                raise FingerprintError(f"Fingerprint matched {employee_id}, but that employee is not registered.")
            if not employee.active:
                raise FingerprintError(f"{employee.name} is marked inactive.")
            return employee
        if line == "NO_MATCH":
            raise NoMatchError("Fingerprint was scanned, but it did not match an enrolled employee.")

    raise FingerprintError("The fingerprint helper finished without a match result.")


def record_clock_event(employee):
    ensure_data_files()
    action = next_clock_action(employee.employee_id)
    event = ClockEvent(
        timestamp=datetime.now().isoformat(timespec="seconds"),
        employee_id=employee.employee_id,
        employee_name=employee.name,
        action=action,
    )
    with open(TIME_CLOCK_LOG_FILEPATH, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=TIME_LOG_HEADERS)
        writer.writerow(event.__dict__)
    return event


def next_clock_action(employee_id):
    last_action = last_clock_action(employee_id)
    return "clock_out" if last_action == "clock_in" else "clock_in"


def last_clock_action(employee_id):
    employee_id = sanitize_employee_id(employee_id)
    action = None
    for event in load_clock_events():
        if event.employee_id == employee_id:
            action = event.action
    return action


def load_clock_events(on_date=None):
    ensure_data_files()
    events = []
    with open(TIME_CLOCK_LOG_FILEPATH, newline="", encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            timestamp = row.get("timestamp", "").strip()
            if on_date and not _timestamp_is_on_date(timestamp, on_date):
                continue
            events.append(
                ClockEvent(
                    timestamp=timestamp,
                    employee_id=row.get("employee_id", "").strip(),
                    employee_name=row.get("employee_name", "").strip(),
                    action=row.get("action", "").strip(),
                    source=row.get("source", "fingerprint").strip() or "fingerprint",
                )
            )
    return events


def recent_clock_events(limit=12, on_date=None):
    return list(reversed(load_clock_events(on_date=on_date)[-limit:]))


def summarize_hours(on_date=None):
    employees = {employee.employee_id: employee for employee in load_employees(include_inactive=True)}
    events = load_clock_events(on_date=on_date)
    summary = {}
    open_sessions = {}

    for event in events:
        employee = employees.get(event.employee_id)
        name = event.employee_name or (employee.name if employee else event.employee_id)
        row = summary.setdefault(
            event.employee_id,
            {"employee_id": event.employee_id, "name": name, "seconds": 0, "status": "Clocked out"},
        )
        timestamp = _parse_timestamp(event.timestamp)
        if not timestamp:
            continue
        if event.action == "clock_in":
            open_sessions[event.employee_id] = timestamp
            row["status"] = "Clocked in"
        elif event.action == "clock_out":
            start = open_sessions.pop(event.employee_id, None)
            if start and timestamp > start:
                row["seconds"] += int((timestamp - start).total_seconds())
            row["status"] = "Clocked out"

    now = datetime.now()
    for employee_id, start in open_sessions.items():
        row = summary.setdefault(
            employee_id,
            {
                "employee_id": employee_id,
                "name": employees.get(employee_id).name if employee_id in employees else employee_id,
                "seconds": 0,
                "status": "Clocked in",
            },
        )
        if now > start:
            row["seconds"] += int((now - start).total_seconds())
        row["status"] = "Clocked in"

    return sorted(summary.values(), key=lambda item: item["name"].lower())


def format_action(action):
    return "Clocked in" if action == "clock_in" else "Clocked out"


def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def secure_fingerprint_files():
    for path in Path(FINGERPRINT_STORAGE_DIR).glob("*.fpdata"):
        _chmod_quiet(path, 0o600)


def _run_helper(args, timeout, on_event=None):
    ensure_data_files()
    helper = find_helper_binary()
    if not helper:
        raise HelperNotFoundError(build_helper_hint())

    command = [helper, *args]
    lines = []
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    selector = selectors.DefaultSelector()
    if process.stdout is not None:
        selector.register(process.stdout, selectors.EVENT_READ)

    try:
        while process.poll() is None:
            for key, _ in selector.select(timeout=0.2):
                line = key.fileobj.readline()
                if line:
                    _record_helper_line(line, lines, on_event)
            if timeout and time.monotonic() - started > timeout:
                process.kill()
                process.wait()
                raise FingerprintError("Fingerprint scan timed out.")

        if process.stdout is not None:
            for line in process.stdout:
                if not line:
                    break
                _record_helper_line(line, lines, on_event)
    finally:
        selector.close()
        if process.poll() is None:
            process.kill()
            process.wait()

    return_code = process.returncode
    if return_code != 0:
        error_line = next((line for line in lines if line.startswith("ERROR|")), "")
        message = error_line.split("|", 1)[1] if "|" in error_line else "\n".join(lines[-4:])
        raise FingerprintError(message or f"Fingerprint helper exited with code {return_code}.")

    return lines


def _record_helper_line(line, lines, on_event):
    line = line.strip()
    if line:
        lines.append(line)
        if on_event:
            on_event(line)


def _write_csv_headers(path, headers):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        csv.DictWriter(csvfile, fieldnames=headers).writeheader()
    _chmod_quiet(path, 0o600)


def _write_csv_rows(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    _chmod_quiet(path, 0o600)


def _employee_to_row(employee):
    return {
        "employee_id": employee.employee_id,
        "name": employee.name,
        "finger": employee.finger,
        "enrolled_at": employee.enrolled_at,
        "active": "1" if employee.active else "0",
    }


def _timestamp_is_on_date(timestamp, on_date):
    parsed = _parse_timestamp(timestamp)
    if not parsed:
        return False
    if isinstance(on_date, date):
        return parsed.date() == on_date
    return parsed.date().isoformat() == str(on_date)


def _parse_timestamp(timestamp):
    try:
        return datetime.fromisoformat(timestamp)
    except (TypeError, ValueError):
        return None


def _chmod_quiet(path, mode):
    try:
        os.chmod(path, mode)
    except OSError:
        pass
