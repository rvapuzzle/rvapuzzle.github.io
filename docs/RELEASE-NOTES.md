# First upgrade — review notes

Based on repository commit `0c82ac5` and the three supplied source files. Payment provider remains Ticket Tailor. No public editing interface or new hosting service.

## Implemented

- Compact teal/orange homepage with real event photography, no stock-image request or remote font dependency.
- Separate event, results, photos, and accessibility pages; permanent event URLs, statuses, and calendar downloads.
- Native keyboard-accessible menu and photo dialog with focus return, ordinary image-link fallback, skip link, readable contrast, and reduced-motion support.
- Host workflows for events, access arrangements, results, and photos on GitHub.com.
- Reusable verified venue names/addresses; safe plain-text rendering and validation before publication.
- Metadata, canonical links, event structured data, organization structured data, social previews, sitemap, and robots file.
- Image resize/compression and responsive sources, deferred below-fold images, reserved image dimensions.
- Daily archival rebuild, failure-safe deployment, and documented rollback.

## Data verification

Venue addresses checked against official venue pages on November 15, 2026:
- Starr Hill: https://starrhill.com/richmond — 3406 West Leigh St, Richmond, VA 23230.
- Basic City: https://www.basiccitybeer.com/copy-of-wboro-2 — 212 West 6th Street, Richmond Southside. No unverified postal code added.

Wheelchair access: organizer confirmation in this conversation. Restrooms and Deaf-specific event arrangements remain unconfirmed.

Existing dates, times, finishing times, photos, and ticket URLs are preserved. In particular, December 29 remains **1–3 PM**, as in the supplied HTML. Please confirm it: the venue's usual Tuesday hours differ, but special events can have different hours. Prices remain “see Ticket Tailor” until supplied. No fabricated offers/prices are inserted into structured data.

## Still requires release verification

- Authenticated repository access or installation of the package; no changes pushed to GitHub from this workspace.
- One-time Pages source change to GitHub Actions and a successful workflow run.
- Manual mobile, screen-reader, and third-party checkout verification; no WCAG certification claimed.
- Host confirmation of written instructions, visual signals, visible timing, restroom details, and other accommodations.
- Search Console ownership verification, sitemap submission, and Rich Results Test after deployment. Search ranking/rich-result inclusion is not guaranteed.
- Review new logo when available; existing logo is optimized and retained.
- Analytics, email signup, automatic Ticket Tailor inventory synchronization, video publishing, bulk photo-description forms, and custom payment processing are not included.

## Maintenance notes

The build deliberately starts from current default-branch content, so queued deployment jobs do not publish an older content commit. Host edits are serialized. A concurrent manual push can cause the edit job to fail safely; rerun after reviewing the latest content.

Generated pages and images live in `_site/`, not the legacy root HTML. Website descriptions are escaped as text, not treated as HTML. Workflow inputs travel via environment JSON rather than shell interpolation. Source photo metadata is removed from generated derivatives; originals remain in the public repository.

## Verification performed in this workspace

- 14 validation and form-operation tests passed, including invalid dates, DST transitions, duplicate IDs, unsafe URLs/paths, missing descriptions, add/edit/access updates, results, and winners-photo association.
- All generated local links, anchors, unique IDs, and image attributes checked across nine pages.
- JavaScript syntax check passed.
- Browser inspection of homepage and event details completed. Keyboard Enter opened a photo, focus moved to Close, Escape closed it, and focus returned to its original link.
- Exact pinned Pillow dependency installed successfully and used for the final build.
- Displayed header logo derivative: 9,986 bytes versus original 6,644,077 bytes. This is an asset-size comparison, not a measured page-load time or Lighthouse score.
- GitHub-hosted workflows have not run yet because authenticated GitHub access is not connected.
