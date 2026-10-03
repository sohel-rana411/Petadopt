# PawHome – Pet Adoption (Django + DRF)

## Run it
```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser        # your admin login
python manage.py seed_pets              # optional: 10 demo pets
python manage.py runserver
```
Site: http://127.0.0.1:8000/ · Admin: /admin/ · API: /api/ · Tests: `python manage.py test`

## Business rules (adoptions/models.py)
1. Only `Available` pets accept applications (form, API and model `clean()` all check).
2. One *pending* request per user per pet (model `clean()` + DB `UniqueConstraint`).
3. Approving a request (admin form or admin action) sets the pet to `Adopted`
   and auto-rejects the other pending requests for that pet, in one transaction.

## Web pages
`/` home · `/pets/` list + search/filter + pagination · `/pets/<id>/` details ·
`/adoptions/apply/<id>/` form · `/adoptions/my-requests/` dashboard ·
`/accounts/{login,register,profile}/` · `/favorites/` (bonus)

## REST API
| Endpoint | Notes |
|---|---|
| `GET/POST /api/pets/`, `GET/PUT/PATCH/DELETE /api/pets/<id>/` | read = public, write = staff only |
| `/api/pets/?search=golden`, `?animal_type=Dog`, `?gender=Male`, `?location=`, `?breed=`, `?name=`, `?status=`, `?page=2` | search, filter, pagination |
| `GET/POST /api/adoptions/`, `GET/PUT /api/adoptions/<id>/` | only the logged-in user's own requests; `status` is read-only (admins change it in Django Admin); only pending requests are editable |
| `POST /api/token/` `{"username","password"}` | returns a token; send `Authorization: Token <key>` |

Example:
```bash
TOKEN=$(curl -s -X POST localhost:8000/api/token/ -d username=rahim -d password=... | python -c "import sys,json;print(json.load(sys.stdin)['token'])")
curl -H "Authorization: Token $TOKEN" -X POST localhost:8000/api/adoptions/ \
  -H "Content-Type: application/json" \
  -d '{"pet":1,"phone":"01700000000","address":"Dhaka","reason":"Love dogs","previous_pet_experience":true}'
```

## Bonus features included
Favorites · web pagination · API pagination · token authentication · pet categories (Dog/Cat/Bird/Rabbit/Other).
