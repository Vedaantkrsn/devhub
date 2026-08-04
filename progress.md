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
- Settings added: `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, `MEDIA_URL`, `MEDIA_ROOT` + `static()` in root urls.py

## Phase 3: Projects Core — ✅ DONE
- ✅ `ProjectForm` (ModelForm, explicit fields, excludes `author`/timestamps)
- ✅ `new_project` view — `@login_required`, `commit=False` → set `author` → `save()` → `save_m2m()` pattern
- ✅ `new_project.html` — `enctype="multipart/form-data"` included
- ✅ Navbar "New Project" link wired
- ✅ Full create flow tested end-to-end
- ✅ `project_detail` view — uses `get_object_or_404(Project, pk=pk)` for clean 404s instead of unhandled 500 crash
- ✅ `project_detail.html` — screenshot, author, category, description, technologies loop, GitHub/demo links (guarded with `{% if %}` since both are optional fields), tags, published date
- ✅ `project_edit` view — `@login_required`, ownership check (`request.user.profile != project.author` → `raise PermissionDenied`), `instance=project` pattern for pre-fill + update
- ✅ `project_edit.html` — same shape as new_project.html
- ✅ `project_delete` view — ownership check, GET shows confirmation template, POST actually deletes + redirects to `home`
- ✅ `project_delete.html` — confirmation page, `btn-danger`/`btn-secondary`, cancel link back to detail
- ✅ Owner-only Edit/Delete buttons on `project_detail.html` — nested `{% if user.is_authenticated %}` → `{% if user.profile == project.author %}`, correctly guards against `AnonymousUser` never having `.profile`
- URL naming: `project_detail`, `project_edit`, `project_delete` all standardized on `pk` as the kwarg (consistent across URL pattern + view signature + redirect calls)

## Phase 2 loose end — ✅ CLOSED: Profile Edit
- `ProfileForm` — ModelForm, explicit fields (`profile_picture`, `bio`, `organization`, `location`, `experience_level`, `skills`, `github_url`, `linkedin_url`, `portfolio_url`), excludes `user`/`joined_date`
- `profile_edit` view — `@login_required`, no `pk`/`username` param, always operates on `request.user.profile` — safe by construction, no ownership check needed since there's nothing to tamper with in the URL
- `profile_page` view — public, takes `username`, looks up via `get_object_or_404(User, username=username)` then `.profile`
- URL ordering: `profile/edit/` placed **before** `profile/<str:username>/edit/` in urls.py — required, since `<str:username>` would otherwise greedily match the literal string "edit"
- Considered changing to `profile/<username>/edit/` for REST-style consistency — deliberately rejected, since it would reintroduce a tamperable URL param requiring a manual ownership check, for zero functional gain over the current parameterless design
- `profile_page.html` — avatar (guarded), bio/org/location (all guarded, optional fields), skills list, GitHub/LinkedIn/portfolio links (guarded), owner-only "Edit Profile" button, list of author's published projects via `profile.projects.all()`
- Navbar "Profile" link wired to `{% url 'profile_page' username=user.username %}`
- Tested: own profile loads, edit pre-fills and saves, `/profile/edit/` routes correctly (not caught as username), other users' profiles show no Edit button

## Phase 4: Homepage Feed — ✅ DONE (core display)
- `home` view — `Project.objects.all().order_by('-published_at')`, newest-first
- `home.html` — X/Twitter-style card layout: author avatar (guarded) + username (linked to `profile_page`) + relative timestamp (`timesince` filter), project title (linked to detail), truncated description (`truncatewords:25`), guarded screenshot, placeholder Like/Comment/Bookmark/Share row (visual only, no functionality yet — that's Phase 5), owner-only three-dot menu placeholder
- Empty-state handled (`{% if projects %}` / `{% else %}`)
- Tested: ordering, truncation, timesince display, avatar links to correct profile

- Still open from Phase 4 (per brief, non-core): global search bar, Popular Technologies / Suggested Developers sections. Hero section and Trending Projects are explicitly V2/future.

## Phase 5: Interactions — 🔧 IN PROGRESS

### Like — ✅ DONE
- `Like` model already had `UniqueConstraint(user, project)` from Phase 1
- `like` view — `@login_required`, `@require_POST`, `get_or_create`/`delete` toggle pattern, returns `JsonResponse({"liked": ..., "likes_count": ...})`
- `home` view — annotates queryset with `is_liked` via `Exists(Like.objects.filter(project=OuterRef("pk"), user=request.user.profile))`, only when `request.user.is_authenticated` — avoids per-project queries (N+1 problem)
- `project_detail` view — single-project version, plain attribute assignment (`project.is_liked = ...`) instead of queryset annotation, since only one object is in play (not a list)
- AJAX via `fetch()` — no page reload, updates icon class (`bi-heart` / `bi-heart-fill`) and count span directly
- Switched from emoji to Bootstrap Icons (`bi-heart`/`bi-heart-fill`) — requires bootstrap-icons CDN link in base.html

### Bookmark — ✅ DONE (toggle only)
- Mirrors Like pattern exactly — `Bookmark` model, `bookmark` view, `is_bookmarked` annotation, matching JS handler
- 🔲 **"My Saved Projects" page still not built** — bookmark toggle works, but no page lists them yet. Plan: `Bookmark.objects.filter(user=request.user.profile)` or `Project.objects.filter(bookmarks__user=request.user.profile)`, reuse card markup from home feed

### Comment — ✅ DONE
- `Comment` model — `Meta.ordering = ["-created_at"]`, `related_name="comments"`
- `CommentForm` — ModelForm, single `content` field, custom Textarea widget/placeholder
- `comment` view — `@login_required`, `@require_POST`, `commit=False` → set `author`/`project` → save, returns JSON with comment data + `comment_count`
- `project_detail` view — **removed accidental `@login_required`** (was blocking guests from viewing projects at all, violating the brief's "guests browse freely" rule). Guest vs. auth branching now matches the `home` view's pattern: `is_liked`/`is_bookmarked` default to `False` for anonymous users instead of crashing on `.profile`
- `select_related("author", "author__user")` on comment queryset — avoids extra queries per comment when rendering author info
- AJAX comment submission — posts via `fetch()` + `FormData`, inserts new comment into DOM live via `insertAdjacentHTML`, resets form, removes "no comments yet" placeholder
- **Fixed: XSS gap** — raw `data.content` was being inserted as unescaped HTML in the JS template string; a comment containing HTML/script tags would have rendered as live markup instead of text. Escaped before insertion.
- **Fixed: stale comment count** — JS wasn't updating `#comment-count-{{ project.pk }}` after posting; now uses `data.comment_count` from the view response

### Still open in Phase 5 / v1
- 🔲 My Saved Projects page (bookmark list view + template)
- 🔲 Share button — brief only requires JS clipboard copy of project URL, no backend needed
- 🔲 Triple-dot dropdown menu — currently a static `⋮` placeholder; needs real Bootstrap dropdown with Edit/Delete links (owner-only, pages already exist)
- 🔲 Global search bar — categorized results across Project and Profile models; biggest remaining piece, comparable in scope to Phase 3

### Cleanup / known debt
- `like.html` and `bookmark.html` template partials are unused dead files — card markup is duplicated inline in `home.html`/`project_detail.html` instead. Either delete the partials or actually `{% include %}` them to avoid maintaining duplicate button markup across pages.
- Guest interaction UX gap (noted, not yet fixed): if a guest triggers a Like/Bookmark/Comment fetch call, `@login_required` redirects the request server-side, but since it's AJAX, the JS just fails silently instead of prompting login. Not urgent, but worth fixing before this is shown to real guest users.

## Next: Share (quick) → Triple-dot menu → Saved Projects page → Search bar

## Known gotchas hit (additional)
- `redirect()` and `{% url %}` calls must match the exact kwarg name used in the URL pattern (`pk` vs `project_id`) — same class of bug as the earlier `login`/`user_login` mismatch
- Templates silently render blank for nonexistent model attributes (e.g. `{{ project.created_at }}` when the field is actually `published_at`) — no error, just empty output, easy to miss
- Delete must never happen on GET — only POST — to avoid accidental deletion via prefetch/crawler/link preview

## Not yet done (still open)
- Profile edit view (fill in bio/skills/links after bare registration)
- Reciprocal "Already have an account? Login" link on register.html
- Multi-app split decision — deferred, revisit later
- `get_category_display` for human-readable category label (optional polish)

## Next: Phase 5 — Interactions
- Wire up Like, Comment, Bookmark, Share buttons for real (currently static placeholders on feed cards)