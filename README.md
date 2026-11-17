# RVA Puzzle League website

Accessible, static GitHub Pages website. Visitors see event information; hosts edit through forms on **GitHub.com → Actions**. Ticket Tailor remains the registration provider.

## One-time installation

1. Add the upgrade files to this repository, retaining `pics/`, `logo.png`, `favicon.ico`, `CNAME`, and `timer.html`. The original root HTML/CSS/JS are retained as a fallback until you switch Pages to Actions.
2. In **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**. Keep the existing custom domain `rvapuzzleleague.com` and HTTPS setting.
3. In **Actions**, run **Build and publish website** on `main`. The workflow must be on the default branch to appear.
4. Confirm the deploy job succeeds, then visit your custom domain.
5. Give event hosts repository write access through the repository's normal collaborator settings. If branch protection prevents the publishing bot from committing, have the repository maintainer configure an approved content-edit process; do not disable protections casually.

The workflow requests write access only where required. It uses GitHub's built-in token, not a personal access token. Host forms run on the default branch. Publishing is explicitly called after each edit because a bot-authored commit does not trigger another push workflow.

See [Host guide](docs/HOST-GUIDE.md), [Access checklist](docs/EVENT-ACCESS.md), and [Release notes](docs/RELEASE-NOTES.md).

## Files

- `content/events.json`: event content, status, and event-specific accessibility.
- `content/venues.json`: reusable venue names and addresses.
- `content/results.json`: text results and winners photos.
- `content/photos.json`: gallery photos, descriptions, and optional event association.
- `content/site.json`: site URL, logo path, email, brand name.
- `src/style.css`, `src/script.js`: new site presentation and interaction.
- `tools/build.py`: HTML, calendar, sitemap, and image generation.
- `.github/workflows/`: host forms and publishing.
- `_site/`: generated deployment output; ignored by Git.
- Root `index.html`, `style.css`, `script.js`: legacy fallback, **not** the source for the upgraded site.

## Local development

Python 3.12 or newer is required.

```
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python tools/build.py
python tools/check.py
python -m http.server 8000 --directory _site
```

`python tools/build.py --now 2026-11-15T19:00` produces a reproducible preview. Production builds use the actual America/New_York time, including daylight saving. A daily workflow moves completed events into the archive; scheduled runs can be delayed by GitHub. GitHub may disable scheduled workflows in inactive public repositories; re-enable them in Actions if necessary.

## Scope and limitations

No public admin page, database, custom payment processing, tracking pixels, or accessibility overlay. No secrets or attendee data belong in the repository. Automated checks and keyboard browser checks do not establish WCAG conformance. Manual screen-reader, physical-device, and Ticket Tailor checkout testing remain release tasks.

Switching Pages to Actions deploys only `_site`, leaving source files out of the published website. This repository itself is public: original uploads remain public in GitHub history. Upload only photos cleared for publication; remove location metadata before uploading if necessary. Generated WebP derivatives omit source metadata.

The existing standalone `timer.html` is preserved unchanged. It is a host tool and has not been included in the accessibility claim or redesigned. Do not describe visual timing at an event as confirmed merely because this file exists.
