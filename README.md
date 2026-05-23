# Hopkins Inventory Management System

![Hopkins Logo](assets/HPS.png)

## Overview

A comprehensive **inventory management solution** for Hopkins Plaster Studio, built with Python and Tkinter.

---

## Features

- **Full-screen User Interface**: Clean, modern UI designed for efficiency
- **Fingerprint Clock In/Out**: Employee attendance flow using the WA28/CS9711 reader
- **CSV Data Management**: View and edit inventory data in tabular format
- **Interactive Tables**:
  - Sort and filter data
  - Direct in-app editing
  - Alternating row colors for readability
- **Data Visualization**: Display inventory information in an easy-to-read format
- **Editing Capabilities**: Add, edit, or delete inventory records
- **Automatic Data Validation**: Ensures data integrity during editing

## Installation

### Prerequisites

- Python 3.x
- Tkinter (usually included with Python installation)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/sedhain-pankaj/Hopkins-Inventory-Management.git
   cd Hopkins-Inventory-Management
   ```

2. Install the Python runtime packages e.g. on Debian/Ubuntu:
   ```
   sudo apt install python3-tk
   ```
3. Run the application:
   ```
   python index.py
   ```

## Fingerprint Clock Setup

The WA28 reader appears as `2541:0236` and is supported by the bundled
`../rust-hps-inventory/libfprint-CS9711` fork after the Rust split. The clock
system stores app-local templates in `data/fingerprints/`; it does not enroll
fingerprints for Linux login.

Build the helper once:

```bash
sudo apt install meson ninja-build pkg-config libglib2.0-dev libgusb-dev libopencv-dev doctest-dev
cd ../rust-hps-inventory
meson setup libfprint-CS9711/build libfprint-CS9711 -Ddrivers=cs9711 -Ddoc=false -Dgtk-examples=false -Dintrospection=false -Dinstalled-tests=false -Dudev_rules=disabled -Dudev_hwdb=disabled
ninja -C libfprint-CS9711/build examples/employee-clock-helper
```

If you build the helper somewhere else, set `HPS_FINGERPRINT_HELPER` to the
full path of the `employee-clock-helper` binary before running the app.

Enroll an employee:

```bash
python3 admin_enroll_employee.py EMP001 "Employee Name" --finger right-index
```

Then open the app and choose **Clock In / Out**. The page starts the
fingerprint scan automatically, identifies the employee, and writes the event
to `data/time_clock_log.csv`. The **Hours Worked** page summarizes today's
clocked time from that log.

## Rust/Tauri Kiosk App

The Rust/Tauri kiosk rewrite now lives beside this Python legacy app at
`../rust-hps-inventory`.

## Project Structure

```
Hopkins-Inventory-Management/
├── index.py                    # Application entry point
├── admin_enroll_employee.py    # One-off employee fingerprint enrollment
├── Utilities/
│   ├── fingerprint_service.py  # Employee registry, helper wrapper, and clock log
│   └── utils.py                # General UI helpers
├── pages/
│   ├── clock_in_out.py         # Fingerprint clock page
│   ├── hours_worked.py         # Attendance summary
│   └── preview_csv.py          # CSV preview and editing functionality
├── assets/
│   ├── HPS.png          # Application logo
│   └── cornice_rate.csv # Sample inventory data
└── data/                # Local generated employee/log data, ignored by git
```

---
