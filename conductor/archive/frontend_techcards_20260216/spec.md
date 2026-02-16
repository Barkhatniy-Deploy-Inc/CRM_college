# Specification: Technological Cards Constructor

## Goal
Implement a comprehensive interface for teachers to create, manage, and export lesson technological cards (lesson plans).

## Core Features
1.  **Techcard List:** View previously created cards with filtering by subject/date.
2.  **Advanced Editor:**
    *   Basic Info: Topic, Group, Lesson Type, Pedagogical Technologies.
    *   Objectives: Learning, Developing, Educational goals.
    *   Expected Outcomes & Equipment.
    *   Resources: Literature, online sources.
3.  **Interactive Lesson Stages:**
    *   Dynamic table for stages (Duration, Teacher activity, Student activity, Competencies).
    *   Reordering and adding/removing stages.
4.  **Auto-fill Integration:**
    *   Link card to a schedule slot (`lesson_id`).
    *   Fetch topic and teacher from `Schedule Service`.
5.  **Document Export:**
    *   Generate and download `.docx` files using the backend service.

## Visual Design
*   MD3 Tabbed interface for large forms.
*   Interactive tables for stages.
*   Glassmorphism consistency.

## Technical Details
*   Backend: `Techcard Service` (Port 8001/api/techcard).
*   State: `techcard.js` store.
