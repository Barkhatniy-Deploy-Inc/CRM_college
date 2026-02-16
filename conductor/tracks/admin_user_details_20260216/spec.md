# Specification: Advanced User Profile & Tech Details

## Goal
Provide administrators with detailed technical information about users, including their connectivity and device environment, to improve security monitoring and support.

## Core Features
1.  **Technical Data Collection:**
    *   Last IP Address (masked for privacy where appropriate, or full for admins).
    *   Last Browser (extracted from User-Agent).
    *   Device Type (Mobile, Tablet, Desktop).
2.  **User Profile Modal:**
    *   Detailed view of a single user.
    *   Visual indicators for devices.
    *   Connection history summary.

## Backend Requirements
- Update `UserResponse` schema in Auth Service.
- Enhance `get_user` logic to join with `LoginHistory`.
- Implement a parser for User-Agent strings (or simple logic for device detection).

## Frontend Requirements
- `UserDetailModal.vue` component.
- Integration into `UsersManagementView.vue` (view action).
- Device icons in `AppIcon.vue` (if missing).

## Visual Style
- Consistency with Glassmorphism and MD3.
- Use of badges for technical metadata.
