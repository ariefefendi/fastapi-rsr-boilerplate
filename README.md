# FastAPI Core API

A RESTful API built with **FastAPI**, **SQLAlchemy 2.0** and **MySQL 8**, organized with a
**Router → Service → Repository** architecture and fully containerized with Docker.

The `Units` module is a port of a Laravel controller/model (`UnitsController`, `Units`) and serves as the
reference implementation for new modules.

## Tech Stack

- Python 3.12
- FastAPI + Uvicorn (development) / Gunicorn with Uvicorn workers (production)
- SQLAlchemy 2.0 with `mysqlclient`
- Pydantic v2
- MySQL 8.0
- Docker & Docker Compose

## Project Structure

```
.
├── app/
│   ├── main.py                    # FastAPI app and exception handlers
│   ├── database.py                # Engine, session, Base, get_db
│   ├── exceptions.py              # Domain exceptions (NotFoundError, UniqueViolationError)
│   ├── models/                    # SQLAlchemy models (tables)
│   ├── schemas/                   # Pydantic request/response schemas
│   │   └── common.py              # Generic DataTableResponse[T]
│   ├── routers/                   # HTTP layer only (controllers)
│   ├── services/
│   │   ├── base.py                # Generic BaseService (CRUD logic)
│   │   ├── units_service.py
│   │   ├── uuid_service.py
│   │   └── short_id_service.py
│   ├── repositories/
│   │   ├── base.py                # Generic BaseRepository (queries)
│   │   └── units_repository.py
│   └── dependencies/              # Auth and dependency wiring
├── db/
│   └── seed_units.sql             # 10 dummy rows for the Units module
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── rebuild.ps1                    # No-cache rebuild + restart (Windows / PowerShell)
├── rebuild.sh                     # No-cache rebuild + restart (Linux / macOS)
├── urls.ps1                       # Print app URLs and check their HTTP status (PowerShell)
├── requirements.txt
├── .env.example
└── .dockerignore
```

> The `app/` folder must sit **next to** `Dockerfile` and `docker-compose.yml`. The compose file mounts the project
> folder into the container (`.:/app`), so the container sees exactly the folder layout you have on the host.

## Architecture

| Layer | Responsibility | Must not |
|---|---|---|
| **Router** | Parse the request, call the service, return the response | Contain queries or business logic |
| **Service** | Business rules (unique checks, ID/reference generation, defaults); raises domain exceptions | Know about HTTP |
| **Repository** | All database queries, including soft-delete filtering | Contain business rules |

Domain exceptions raised by services are translated into HTTP responses in `app/main.py`.

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Setup

```bash
cp .env.example .env     # Windows PowerShell: copy .env.example .env
# edit .env and set the passwords
docker compose up --build
```

Once running:

- API: http://localhost:8000
- Interactive docs (Swagger UI): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DB_DATABASE` | Database name | `djangocore` |
| `DB_USERNAME` | Application database user | `djangocore_app` |
| `DB_PASSWORD` | Application user password | *required* |
| `MYSQL_ROOT_PASSWORD` | MySQL root password | *required* |
| `DB_HOST` | Set to `db` by `docker-compose.yml` | `db` |
| `DB_PORT` | Set to `3306` by `docker-compose.yml` | `3306` |

Never commit `.env`. It is listed in `.gitignore` and `.dockerignore`.

### Database Access

```bash
docker compose exec db mysql -uroot -p
```

## Checking the URLs

| Purpose | URL |
|---|---|
| App root | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI schema (JSON) | http://localhost:8000/openapi.json |
| Units endpoint | http://localhost:8000/master-data/units |

Print all of them with their HTTP status using the helper script (PowerShell):

```powershell
.\urls.ps1
# custom port, e.g. when the compose port mapping is "8001:8000":
.\urls.ps1 -BaseUrl http://localhost:8001
# if blocked by the execution policy:
powershell -ExecutionPolicy Bypass -File .\urls.ps1
```

Example output:

```
Keperluan            URL                                    Status
---------            ---                                    ------
Root app             http://localhost:8000/                    404
Swagger UI           http://localhost:8000/docs                200
ReDoc                http://localhost:8000/redoc               200
Skema OpenAPI (JSON) http://localhost:8000/openapi.json        200
Endpoint Units       http://localhost:8000/master-data/units   200
```

| Status | Meaning |
|---|---|
| `200` | The URL is reachable |
| `404` on the root | Expected. No route is defined for `/` |
| `500` on the Units endpoint | Usually the `units` table is missing or the database connection failed. Check `docker compose logs --tail 50 web` |
| `DOWN` | The container is not running or port 8000 is not published. Check `docker compose ps` |

`/docs` and `/redoc` can load even when the table is missing, because they only read the API schema.

## Rebuilding and Restarting (No Cache)

Use the helper scripts to rebuild the image from scratch and recreate the containers.

**Windows (PowerShell):**

```powershell
.\rebuild.ps1
# if blocked by the execution policy:
powershell -ExecutionPolicy Bypass -File .\rebuild.ps1
```

**Linux / macOS:**

```bash
./rebuild.sh
```

What the scripts do:

1. `docker compose down --remove-orphans`
2. `docker compose build --no-cache --pull` (ignores all cached layers and re-pulls the base image)
3. `docker compose up -d --force-recreate --renew-anon-volumes`
4. `docker compose ps`, then follow the `web` logs (Ctrl+C leaves the containers running)

| PowerShell | Shell | Effect |
|---|---|---|
| `-Prune` | `--prune` | Also clear Docker's build cache (`docker builder prune -f`) |
| `-Fresh` | `--fresh` | Also **delete the MySQL volume** (asks for confirmation). All database data is lost |
| `-NoLogs` | `--no-logs` | Do not follow logs at the end |

One-liner without the scripts:

```powershell
docker compose down --remove-orphans; docker compose build --no-cache --pull; docker compose up -d --force-recreate
```

### When is a rebuild needed?

| Change | Action |
|---|---|
| Python code under `app/` | Nothing. The source is mounted and Uvicorn runs with `--reload` |
| `requirements.txt`, `Dockerfile`, `entrypoint.sh` | Rebuild (`.\rebuild.ps1`) |
| `.env`, `docker-compose.yml` | `docker compose up -d --force-recreate` |
| `MYSQL_ROOT_PASSWORD` / `DB_PASSWORD` after the first start | `.\rebuild.ps1 -Fresh`. MySQL only applies these on first initialization of the volume |

## Database Schema

The `units` table is **not** created automatically. If you are reusing the Laravel database, the table
already exists. Otherwise, create it manually using the steps below (or set up
[Alembic](https://alembic.sqlalchemy.org/) migrations; a commented `alembic upgrade head` hook is already
present in `entrypoint.sh`).

Expected columns:

| Column | Type | Notes |
|---|---|---|
| `id` | `VARCHAR(36)` | Primary key (UUID) |
| `reference` | `VARCHAR(20)` | Public identifier, e.g. `UNA1B2C` |
| `code` | `VARCHAR(20)` | Unique |
| `name` | `VARCHAR(50)` | |
| `description` | `VARCHAR(255)` | Nullable |
| `is_active` | `BOOLEAN` | Defaults to `true` |
| `created_at` | `DATETIME` | |
| `updated_at` | `DATETIME` | |
| `deleted_at` | `DATETIME` | Nullable (soft delete) |

### Creating the Table Manually

Use this when the API logs `Table '<database>.units' doesn't exist`
(`sqlalchemy.exc.ProgrammingError ... 1146`), or after resetting the database with `.\rebuild.ps1 -Fresh`,
which removes all tables.

**1. Make sure the containers are running**

```bash
docker compose up -d
```

**2. Open the MySQL shell as root**, directly in the application database. Use the values from your `.env`:
the password is `MYSQL_ROOT_PASSWORD` and the database name is `DB_DATABASE`.

```bash
docker compose exec db mysql -uroot -p <DB_DATABASE>
```

For example, with `DB_DATABASE=fastapicore`:

```bash
docker compose exec db mysql -uroot -p fastapicore
```

**3. Paste and run the SQL:**

```sql
CREATE TABLE units (
  id          VARCHAR(36)  NOT NULL PRIMARY KEY,
  reference   VARCHAR(20)  NOT NULL,
  code        VARCHAR(20)  NOT NULL,
  name        VARCHAR(50)  NOT NULL,
  description VARCHAR(255) NULL,
  is_active   TINYINT(1)   NOT NULL DEFAULT 1,
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at  DATETIME     NULL,
  UNIQUE KEY units_code_unique (code),
  KEY units_reference_index (reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**4. Verify the table**, then leave the shell:

```sql
SHOW TABLES;
DESCRIBE units;
exit
```

**5. Restart the web container** so the API starts with a fresh database connection:

```bash
docker compose restart web
```

**6. Test it.** Open http://localhost:8000/docs and call `POST /master-data/units` with:

```json
{ "code": "KG", "name": "Kilogram" }
```

The response should be `{"result": "OK"}`, and `GET /master-data/units` should list the new record.

> Do not paste real passwords into chats, tickets or commits. Keep them in `.env` only.

### Seeding Dummy Data (Units)

`db/seed_units.sql` inserts **10 sample units** (Kilogram, Gram, Liter, Milliliter, Meter, Centimeter, Pieces,
Box, Dozen, Pack). One record (`DZN`) is inactive and one (`PACK`) has no description, which is handy for testing
filters and nullable fields.

The table must already exist (see [Creating the Table Manually](#creating-the-table-manually)) and the `db`
container must be running.

**Windows (PowerShell):**

```powershell
Get-Content -Raw db\seed_units.sql | docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"'
```

**Linux / macOS:**

```bash
docker compose exec -T db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' < db/seed_units.sql
```

The password and database name are read from the container's own environment, so nothing sensitive is typed
on the command line. A `Using a password on the command line interface can be insecure` warning from MySQL is
harmless.

**Verify:**

```powershell
docker compose exec db sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE" -e "SELECT reference, code, name, is_active FROM units ORDER BY reference;"'
```

Or call the API: `GET http://localhost:8000/master-data/units` should return `"RecordsTotal": 10`.

Notes:

- The script is safe to run repeatedly. It uses `INSERT IGNORE`, so rows whose `id` or `code` already exist are skipped.
- If you already created a unit with the same `code` (for example `KG`), that row is skipped and fewer than 10 rows are added.
- All seeded references start with `UNSD`. To remove only the dummy rows, run this in the MySQL shell
  (see [Creating the Table Manually](#creating-the-table-manually) for how to open it):

  ```sql
  DELETE FROM units WHERE reference LIKE 'UNSD%';
  ```

## API Endpoints — Units

Base path: `/master-data/units`

| Method | Path | Description |
|---|---|---|
| `GET` | `/master-data/units` | Server-side datatable. Query: `filtertext`, `start` (default 0), `length` (default 10) |
| `GET` | `/master-data/units/select?reference=...` | Get a single unit by reference |
| `POST` | `/master-data/units` | Create a unit |
| `PUT` | `/master-data/units` | Update a unit (`id` in the request body) |
| `DELETE` | `/master-data/units?reference=...` | Soft delete a unit |

### Examples

Create:

```bash
curl -X POST http://localhost:8000/master-data/units \
  -H "Content-Type: application/json" \
  -d '{"code": "KG", "name": "Kilogram", "description": "Weight unit"}'
```

List with search:

```bash
curl "http://localhost:8000/master-data/units?filtertext=kilo&start=0&length=10"
```

Datatable response shape:

```json
{
  "RecordsTotal": 1,
  "RecordsFiltered": 1,
  "Data": [ { "id": "...", "reference": "UN...", "code": "KG", "name": "Kilogram" } ]
}
```

### Error Format

Validation errors keep the same format as the original Laravel API (HTTP 422):

```json
{
  "result": "VALIDATION_ERROR",
  "errors": { "code": ["The code has already been taken."] }
}
```

A missing record returns HTTP 404 with `{"detail": "Data tidak ditemukan"}`.

## Adding a New Module

Using `categories` as an example:

1. `app/models/categories.py`: model with `id`, `reference`, `created_at`, `deleted_at` columns plus your own.
2. `app/schemas/categories.py`: `CategoryCreate`, `CategoryUpdate` (must include `id`), `CategoryOut`.
3. `app/repositories/categories_repository.py`:

   ```python
   class CategoriesRepository(BaseRepository[Categories]):
       model = Categories
       search_fields = ("code", "name")
   ```

4. `app/services/categories_service.py`:

   ```python
   class CategoriesService(BaseService[Categories, CategoryCreate, CategoryUpdate]):
       reference_prefix = "CT"
       unique_fields = ("code",)
   ```

5. `app/dependencies/categories.py` and `app/routers/categories.py`: copy the Units pattern.
6. Register the router in `app/main.py` with `app.include_router(...)`.

Override the `_normalize` hook in a service for default values or data transformations.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `failed to calculate checksum ... "/requirements.txt": not found` | `requirements.txt` is missing from the build context. Run the command from the folder that contains `docker-compose.yml`, and check the file is not named `requirements.txt.txt` (Windows hides extensions) |
| `Access denied for user '...'` (MySQL error 1045) | The user or password in `.env` differs from what MySQL created when the volume was first initialized. Reset with `.\rebuild.ps1 -Fresh` (deletes data), or fix the user with `ALTER USER` as root, then `docker compose restart web` |
| `ModuleNotFoundError: No module named 'app'` | The `app/` folder is missing or nested one level too deep. `app/main.py` must exist next to `Dockerfile`. Check with `docker compose run --rm --no-deps --entrypoint "" web ls -R /app/app` |
| `exec /usr/local/bin/entrypoint.sh: no such file or directory` | `entrypoint.sh` has Windows (CRLF) line endings. The Dockerfile strips them with `sed`; if you edited the Dockerfile, keep that line |
| `Table '<database>.units' doesn't exist` | The table has not been created. Follow [Creating the Table Manually](#creating-the-table-manually), then run `docker compose restart web` |
| New DB password has no effect | MySQL only reads the password variables when initializing an empty volume. Use `.\rebuild.ps1 -Fresh` (this deletes data) |
| Changes to Python code not reflected | Make sure the `.:/app` volume is present and the container runs the `development` target |

## Notes

- **Authentication is a stub.** `app/dependencies/auth.py` currently allows every request. Replace it with a real
  implementation (JWT, session, OAuth2) before deploying.
- **Soft deletes are manual.** SQLAlchemy has no built-in equivalent of Laravel's `SoftDeletes`; the repository
  filters `deleted_at IS NULL` on every query.
- **Unique checks include soft-deleted rows**, matching Laravel's `unique` rule. To allow reusing codes of deleted
  records, filter `deleted_at` in `BaseRepository.exists_by`.
- **`UuidService` and `ShortIdService` are reimplementations.** UUIDs use `uuid4`; short IDs are a prefix plus random
  uppercase alphanumerics, without a collision check.

## Production

The compose file uses the `development` target (hot reload, source mounted as a volume). For production:

1. Set `target: production` for the `web` service.
2. Remove the `.:/app` volume.
3. Do not publish the MySQL port (`3306`) to the host.

## Credits

Based on the _*Fastapi RSR Boilerplate Docker Starter Kit*_ by **Arif Efendi** (© 2021-2026).
