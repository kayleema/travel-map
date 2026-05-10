# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
python manage.py runserver

# Apply migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Run tests
python manage.py test

# Run a single test
python manage.py test travelregistration.tests.TestClassName.test_method_name

# Compile i18n translations
python manage.py compilemessages

# Update i18n translation source files
python manage.py makemessages -l ja
```

## Architecture

This is a Django 4.2 app for tracking personal travel across geographic locations. Users log their relationship to each location (lived, stayed, walked, passed through) and view results on an interactive map.

**Django apps:**
- `travelregistration/` — the only app; contains all models, views, serializers, and admin config
- `travelmap/` — project config (settings, root URLs, WSGI/ASGI)

**URL structure:**
- `/` — homepage map (login required)
- `/update/<location_name>` — form to update status for a location
- `/api/locations`, `/api/regions`, `/api/locationentries` — DRF REST API (authenticated)
- `/accounts/` — allauth authentication routes
- `/admin/` — Django admin

**Data model:**
- `Region` → groups locations by area, has a display color
- `Location` → a map position with CSS grid coordinates (`display_x`, `display_y`, `display_width`, `display_height`) and corner `border_radius_*` booleans; has English (`name_en`) and Japanese (`name`) names
- `LocationEntry` → join table linking a `User` to a `Location` with a `status` choice (`none`, `lived`, `stayed`, `walked`, `passed`)

**Templates** (`templates/`):
- `travelregistration/homepage.html` — renders the full grid map with inline CSS; location boxes are color-coded by the user's `LocationEntry.status`
- `update.html` — form for changing a location's status
- `account/base_entrance.html` — allauth login/signup base

**Internationalization:** English and Japanese are supported. Translation strings use `{% translate %}` in templates. Locale files live in `locale/`. Use `makemessages` / `compilemessages` to update.

**Settings:** `travelmap/settings.py` is dev (SQLite, `DEBUG=True`, console email). Production uses `travelmap/settings_prod.py` (PostgreSQL via psycopg, additional CSRF trusted origins).
