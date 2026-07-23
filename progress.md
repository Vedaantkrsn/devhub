# DevHub — Progress Log

## Project Overview
Full-stack Django social platform for developers to showcase projects. Single-app structure (`core`). Stack: Django, Bootstrap 5.3, SQLite.

## Architecture Decisions
- **One app only** (`core`) — no premature splitting into multiple apps
- **Profile via OneToOneField** to `User` (not ForeignKey) — enforces exactly one profile per user at DB level
- **Skill model with ManyToManyField** — shared pool of technologies, linked to both `Profile.skills` and `Project.technologies`
- **Project.owner is ForeignKey to Profile** (not M2M) — current requirement is single-owner; team projects (future) will need a separate `Collaborator` model, not a retrofit
- **Like/Bookmark use UniqueConstraint** on `(user, project)` — enforces "one like per user per project" at DB level, not just app logic
- **Manual Profile creation in register view** (not signals) — chosen deliberately for learning visibility over Django "magic"
- **Function-based views throughout** (register, login) — same reasoning, explicit over implicit

## Phase 1: Data Model & Setup — ✅ DONE
- Models built: `Skill`, `Profile`, `Project`, `Like`, `Comment`, `Bookmark`
- Migrations run, admin registered, admin panel checked
- Deferred for now: `Follow`, `Notification` (correctly scoped as V2/future)
- Deferred for now: `MEDIA_URL`/`MEDIA_ROOT` settings, `LOGIN_URL` setting — will need before Phase 3 (New Project needs `@login_required`, project cards need `screenshot.url`)

## Phase 2: Auth & Profile — ✅ DONE
- `SignUpForm` (extends `UserCreationForm`, adds required email)
- `register` view — validates form, creates User, manually creates Profile, logs in, redirects to home
- `user_login` view — uses `AuthenticationForm`
- Logout — Django's built-in `LogoutView`, POST-only (Django 4.1+ requirement), wired via `<form method="post">` in navbar (not `<a href>`, which throws 405)
- Templates: `base.html` (navbar + auth-state conditional), `register.html`, `user_login.html`, `home.html`
- URL names: `register`, `home`, `user_login` (not `login`), `logout`

## Known gotchas hit (for future reference)
- `NoReverseMatch` — happened from `{% url 'login' %}` when the actual url name was `user_login`. Always double check `name=` in urls.py matches `{% url %}` calls exactly.
- `405 on logout` — Django's `LogoutView` requires POST, not GET, since Django 4.1+. Plain `<a>` tags won't work; needs a `<form method="post">` with `{% csrf_token %}`.
- Stale dev server / cached page can make already-fixed code appear broken — always test from a fresh page load before assuming the code is wrong.

## Not yet done (still open)
- Profile edit view (fill in bio/skills/links after bare registration)
- `MEDIA_URL`/`MEDIA_ROOT` in settings.py + static() in root urls.py (needed once images are displayed)
- `LOGIN_URL` in settings.py (needed once `@login_required` is used)
- Reciprocal "Already have an account? Login" link on register.html

## Next: Phase 3 — Projects Core
- Create/edit/delete project posts
- "New Project" form (will need `@login_required`)
- Project detail page