# Implementation Plan: System Audit

## Phase 1: Backend Audit Service Expansion
- [ ] Task: Expand `AuditAction` enum with new system events
- [ ] Task: Implement advanced filtering logic in `audit_service.py`
- [ ] Task: Create admin-only endpoint for global log retrieval

## Phase 2: Frontend Logs Interface
- [ ] Task: Create `SystemLogsView.vue`
- [ ] Task: Implement log filtering UI (Date range, User, Action type)
- [ ] Task: Add JSON metadata inspector for detailed event info

## Phase 3: Integration & Logging Hooks
- [ ] Task: Add logging hooks to Schedule Service (Manual edits & Imports)
- [ ] Task: Add logging hooks to User CRUD operations
- [ ] Task: Implement "Security Alert" logging for unauthorized admin attempts

## Phase 4: Final Polish
- [ ] Task: Optimize DB queries for log retrieval (Add indexes if needed)
- [ ] Task: Final Review and verification
