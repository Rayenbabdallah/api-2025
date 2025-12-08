You are adding security to an existing Flask REST API project using flask-smorest, Blueprints, and Marshmallow schemas. 
The project already includes: specialization.py, course_item.py, schemas.py, db.py, and an app.py that registers the blueprints. 
Data is stored in in-memory dictionaries inside db.py.

I want you to add a full authentication and authorization system using Flask-JWT-Extended.

YOUR TASKS:

1. Create a new resource file: resources/user.py
   - Create routes:
       POST /register
       POST /login
       POST /refresh
   - Use Marshmallow schemas for validation.
   - Store users in db.py inside "users = {}".
   - Each user has:
       id, username, password (hashed), role (admin, professor, student)

2. Add password hashing using werkzeug.security:
   generate_password_hash()
   check_password_hash()

3. Implement JWT authentication:
   - Return access token & refresh token on login.
   - Use @jwt_required for protected endpoints.
   - Add refresh logic using @jwt_required(refresh=True).

4. Add role-based authorization logic:
   - admin can create/delete specializations & course items
   - professor can create course items only
   - student can only read/get data
   - Implement helper function:
       def require_role(*roles):
           checks current user's JWT role
           abort(403) if unauthorized

5. Modify specialization.py and course_item.py
   - Protect post/put/delete routes with @jwt_required() + require_role(…)
   - GET routes stay public.

6. Update db.py to include:
       users = {}
       (optional) user_course_item_ownership = {}
   Ownership:
   - When professor creates a course item, save the owner (user_id).
   - Professor can only update/delete their own items (admin bypasses).

7. Update schemas.py:
   - Add UserRegisterSchema (username, password, role)
   - Add UserLoginSchema (username, password)

8. Update app.py:
   - Initialize JWTManager(app)
   - Register the new user blueprint

9. Ensure all new endpoints appear correctly in Swagger.

10. Keep all code consistent with the existing project style and architecture.

Generate the full updated code for:
- resources/user.py
- updates to db.py
- updates to schemas.py
- updates to app.py
- modifications to specialization.py and course_item.py




Continue from the previous security implementation.

Apply these final role and authentication rules to my existing Flask-Smorest + JWT project (specialization + course_item):

1. When the application starts, create one default admin user manually (in db.py or equivalent). Username: "admin", password: "admin123" (hashed), role="admin".

2. Public registration:
   - Route: POST /register
   - Anyone can register without authentication.
   - The role must ALWAYS be set to "student" regardless of the request body.
   - The user should NOT be allowed to choose their own role.
   - Hash the password before storing.

3. Login:
   - POST /login
   - Return an access token and a refresh token.
   - Tokens must include { "sub": user_id, "role": user_role }.

4. Role update:
   - Route: PUT /user/<user_id>/role
   - Only admins may access this route.
   - The admin can promote/demote users by changing the role to: "student", "professor", or "admin".

5. Authorization:
   - Add decorators or helper logic so:
        - Only admins can modify roles.
        - Admins and professors can create/edit course_items or specializations.
        - Students can only view (GET requests).

6. DO NOT modify or remove any of the existing specialization/course_item logic. Only add authentication and authorization on top of it.

7. Add a @jwt_required() wrapper around all routes.
   - GET routes are allowed for all authenticated roles.
   - POST/PUT/DELETE require professor or admin.
   - Role modification requires admin.

8. Create schemas for:
   - RegisterSchema (username, password)
   - LoginSchema (username, password)
   - RoleUpdateSchema (role)

9. Update Swagger documentation automatically from the changes.

10. Integrate everything cleanly with Flask-Smorest and Marshmallow so that all validation, responses, and documentation work.

Please generate the full updated code:
- db.py (updated with default admin)
- schemas.py (new auth schemas added)
- resources/user.py (new file for register, login, role update)
- app.py (JWT setup added)
- Updated specialization.py and course_item.py (authorization decorators)
- utility function for verifying roles

Make the code fully functional and consistent with my existing structure.
