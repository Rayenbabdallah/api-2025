# API-2025 – Insomnia Collection Setup

Follow these steps to build an Insomnia collection that covers registration, login, role updates, and the specialization/course-item APIs.

## 1. Create Workspace & Environment
1. Open Insomnia → `Create > Design Document/Collection` → name it **API-2025**.
2. Go to `Manage Environments` and set:
   ```json
   {
     "base_url": "http://localhost:5001",
     "access_token": "",
     "refresh_token": ""
   }
   ```
   Adjust `base_url` if your Docker/Flask server runs elsewhere.

## 2. Auth Folder
Create a folder **Auth** with these requests:

1. **Register (Public)**
   - Method/URL: `POST {{ base_url }}/register`
   - JSON body:
     ```json
     {
       "username": "student1",
       "password": "ChangeMe123"
     }
     ```
   - No auth header (anyone can register; role defaults to `student`).

2. **Login**
   - Method/URL: `POST {{ base_url }}/login`
   - Body:
     ```json
     {
       "username": "admin",
       "password": "admin123"
     }
     ```
   - After the request succeeds, run the Insomnia “Manage Environment > Clipboard” helper to set:
     ```json
     {
       "access_token": "{{ _.response.body.access_token }}",
       "refresh_token": "{{ _.response.body.refresh_token }}"
     }
     ```
     (or paste manually from the response).

3. **Refresh Token**
   - Method/URL: `POST {{ base_url }}/refresh`
   - Header: `Authorization: Bearer {{ refresh_token }}`
   - Body: none.
   - Update `access_token` in the environment with the returned value.

4. **Update User Role (Admin only)**
   - Method/URL: `PUT {{ base_url }}/user/{{ user_id }}/role`
   - Header: `Authorization: Bearer {{ access_token }}`
   - Body:
     ```json
     {
       "role": "professor"
     }
     ```
   - Use this to promote a student after registration.

## 3. Specializations Folder
Add four requests; all require `Authorization: Bearer {{ access_token }}`.

1. **List Specializations**
   - `GET {{ base_url }}/specialization`
2. **Get Specialization By ID**
   - `GET {{ base_url }}/specialization/{{ specialization_id }}`
3. **Create Specialization** (admin or professor)
   - `POST {{ base_url }}/specialization`
   - Body:
     ```json
     {
       "name": "Computer Science"
     }
     ```
4. **Update Specialization**
   - `PUT {{ base_url }}/specialization/{{ specialization_id }}`
   - Body:
     ```json
     {
       "name": "Advanced CS"
     }
     ```
5. **Delete Specialization**
   - `DELETE {{ base_url }}/specialization/{{ specialization_id }}`

## 4. Course Items Folder
Again, add `Authorization: Bearer {{ access_token }}` to every request.

1. **List Course Items**
   - `GET {{ base_url }}/course_item`
2. **Get Course Item By ID**
   - `GET {{ base_url }}/course_item/{{ course_item_id }}`
3. **Create Course Item** (admin/professor; professor must own)
   - `POST {{ base_url }}/course_item`
   - Body:
     ```json
     {
       "name": "Algorithms I",
       "type": "core",
       "specialization_id": "{{ specialization_uuid }}"
     }
     ```
4. **Update Course Item**
   - `PUT {{ base_url }}/course_item/{{ course_item_id }}`
   - Body:
     ```json
     {
       "name": "Algorithms II",
       "type": "advanced"
     }
     ```
5. **Delete Course Item**
   - `DELETE {{ base_url }}/course_item/{{ course_item_id }}`

## 5. Using Different Roles
1. Register a new user via **Register**.
2. As admin, call **Update User Role** to promote the new user to `professor` if they must create/edit.
3. Log in with the promoted account, copy the new tokens into the environment, and re-run specialization/course-item requests to verify permissions.

## 6. Tips
- If a request returns `401`, refresh the token or log in again.
- For professor ownership enforcement, create course items with the professor’s token; only that professor (or an admin) can later edit/delete them.
- Duplicate requests in Insomnia to keep separate examples for admins, professors, and students if needed.
