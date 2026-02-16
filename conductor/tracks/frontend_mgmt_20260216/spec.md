# Specification: System Management & Schedule Editor

## Goal
Transform the system into a proactive management tool by implementing full CRUD operations for users, groups, and schedule slots.

## Core Features
1.  **User Management (Admin):**
    *   Create new users (Student, Teacher, Admin).
    *   Edit existing profiles (Role, Group assignment).
    *   Account lifecycle control (Activate/Deactivate).
2.  **Schedule Management (Dispatcher):**
    *   **Group CRUD:** Manage educational groups.
    *   **Auditorium CRUD:** Manage physical spaces.
    *   **Interactive Editor:** Create/Edit/Delete individual class slots.
    *   **Excel Integration:** UI for importing schedule files.
3.  **Audit & Safety:**
    *   Confirmations for critical actions (deletion).
    *   Success/Error toast notifications.

## Technical Details
*   Backend: `Auth Service` (Users), `Schedule Service` (Schedule/Groups/Auditoriums).
*   Shared Components: Modal windows, Form validation.
