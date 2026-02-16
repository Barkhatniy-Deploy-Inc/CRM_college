# Specification: Frontend Initialization

## Goal
Replace the existing frontend with a modern Vue 3 + Vite setup, establishing a solid foundation for the CRM College system and integrating it with the existing backend services.

## Scope
- Removal of old frontend code.
- Initialization of a new Vue 3 project using Vite.
- Setup of state management (Pinia) and routing (Vue Router).
- Basic UI shell based on Material Design 3 guidelines.
- Implementation of a login page and authentication flow using the existing Auth Service.

## Technical Requirements
- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Language:** JavaScript
- **Store:** Pinia
- **Router:** Vue Router
- **CSS:** Tailwind CSS or plain CSS with MD3 variables.
- **Testing:** Vitest for unit tests.

## Security Considerations
- Secure storage of JWT tokens (HttpOnly cookies preferred, handled by backend).
- Frontend validation of input fields.
- Protected routes for authenticated users.
