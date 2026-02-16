# Specification: System Audit & Logging

## Goal
Implement a centralized system for tracking critical user actions and system events to ensure security and accountability.

## Audit Scope
Track the following actions:
1.  **Auth Events:** Login, Logout, Password Change, Failed Login attempts.
2.  **User Management:** Creating/Updating/Deleting users, changing roles or groups.
3.  **Schedule Changes:** Manual edits to slots, Excel imports, bulk deletions.
4.  **Techcard Actions:** Creation and export of documents.
5.  **Security:** Unauthorized access attempts to admin routes.

## Backend Requirements
- Use existing `AuditLog` model in Auth Service.
- Implement `GET /api/users/audit-log/all` with:
    - Pagination (`page`, `limit`).
    - Filters: `user_id`, `action_type`, `date_from`, `date_to`.
    - Search: IP address or metadata content.

## Frontend Requirements
- `SystemLogsView.vue` in Admin feature.
- Visual distinctiveness for different event severities (INFO, WARNING, CRITICAL).
- Infinite scroll or pagination for log viewing.
- Detailed view for metadata (JSON view).

## Visual Style
- MD3/Glassmorphism consistency.
- Terminal-style typography for log entries.
