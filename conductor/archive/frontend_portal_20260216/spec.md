# Specification: Student Portal (Dashboard & Schedule)

## Goal
Implement a functional and visually appealing student dashboard and schedule view integrated with the backend Schedule Service.

## Core Features
1.  **Dashboard (Home):**
    *   Dynamic greeting based on user name and time of day.
    *   "Upcoming Classes" widget showing the next 2-3 lessons for the current day.
    *   User status card (Role, Group, Account Status).
2.  **Schedule View:**
    *   Grid/List layout for weekly schedule.
    *   Date filtering (previous/next week).
    *   Group filtering (for admins/teachers) or automatic filtering for students.
    *   Class details (Subject, Teacher, Auditorium, Time).
3.  **State Management:**
    *   Pinia store for schedule data (`schedule.js`).
    *   Caching fetched schedule data to reduce API calls.

## Visual Design
*   Follow MD3 (Material Design 3) guidelines.
*   Glassmorphism effects for cards and widgets.
*   Responsive layout (Mobile-first).
*   Transitions between dashboard and schedule views.

## Technical Integration
*   Backend Service: `Schedule Service` (Port 8000/api/schedule).
*   Authentication: JWT (via `Auth Service`).
