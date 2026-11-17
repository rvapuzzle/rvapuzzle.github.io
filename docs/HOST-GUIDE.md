# Updating the website on GitHub.com

You never need to edit the public website or copy an HTML event card.

## Add an event

1. Open the repository's **Actions** tab.
2. Select **Host · Add or edit event**, then **Run workflow**. Use `main`.
3. Choose **Add**. Enter a unique ID such as `2027-01-12-basic-city`. This becomes its permanent page address.
4. Fill the title, date (`2027-01-12`), start/end times (`19:00`, `21:00`, Richmond time), and Ticket Tailor link.
5. Choose a saved venue: `starr-hill` is Scott’s Addition; `basic-city` is Richmond Southside. This fills the verified name/address. For another venue, choose custom and provide name/address.
6. Add a price label that explains whether pricing is per team or person. Include mandatory fees in your public description where applicable. Blank description uses the existing standard competition rules.
7. Run the workflow. Wait for **edit** and **publish** to finish green. The run summary confirms validation; the deploy job links to the site.
8. Use **Host · Update event accessibility** to confirm arrangements for this particular event. New events do not inherit unverified promises.

## Edit, cancel, postpone, or mark sold out

Use the same form with **Edit** and the exact event ID from its URL. Blank text fields retain their existing values. `Keep current` leaves a choice unchanged. Enter `CLEAR` to remove an optional address, price, or description (description is required, so clearing it will fail validation). Use a new valid description instead.

A changed date keeps the same permanent event ID and URL. Enter both times when changing the schedule. Dates/times must be local Richmond time. Overnight events are not supported by this form; ask the maintainer to edit both full dates in the content file.

Canceled, postponed, and past events do not show an active registration button. Sold-out events remain visible. Changing the website status does **not** change Ticket Tailor: update the ticket listing there too. Calendar files already imported by attendees are not subscriptions and will not automatically update; communicate schedule changes separately.

## Accessibility

Use **Host · Update event accessibility**. Each feature has four choices:

- `Keep current`: do not change it.
- `confirmed`: the host/venue has verified it for this event.
- `unavailable`: it is not offered.
- `not_confirmed`: it has not been verified.

Notes are public. Describe arrangements and practical information, not attendees' diagnoses or private requests. `CLEAR` removes old notes. Wheelchair entry, restrooms, written instructions, visual signals, visible timing, and assistive listening are separate questions.

## Results

Run **Host · Publish results** with the date, optional team names, and all three finishing times. Write times like `38m 53s`. Reusing the date updates its results and retains attached winners photos. This date-based workflow supports one results set per day.

## Photos

1. On the repository **Code** tab, open `pics` (or a subfolder).
2. Choose **Add file → Upload files** and upload JPG, PNG, or WebP images. Use descriptive filenames such as `2027-01-12-first-place.jpg`; keep individual files under GitHub's browser upload limit.
3. Commit the upload to `main`. This stores the file but does not automatically add it to the gallery.
4. Run **Host · Publish or update photo**. Enter the exact path, e.g. `pics/2027-01-12-first-place.jpg`.
5. Write a short factual image description. Describe the team/activity without guessing identities or emotions. Add an optional visible caption.
6. For an event gallery, include the event ID. Leave results date blank.
7. For a podium photo, enter the results date and placement. Publish text results first. This attaches it to results instead of the gallery; run again without a results date if you also want it in the gallery.

Repeat for each photo. Uploading several files together is fine; descriptions are entered one photo at a time. Upload browser-supported image formats rather than HEIC. Images are resized and compressed automatically, with full-size viewing capped at 1600 pixels. To remove a published photo, ask the maintainer to remove its entry from `content/photos.json` (or clear the matching results photo); deletion is not in the first-version forms.

## If something fails

Open the red workflow run, then the failed step. Messages explain missing fields, invalid dates, unknown IDs, and missing photo files. A failed build does not replace the live site. If content was saved but deployment failed, correct the problem and rerun **Build and publish website**.

For an accidental published edit, ask the maintainer to revert the corresponding `Update … through host form` commit, then run **Build and publish website**. Do not delete events to hide cancellations; preserve their pages and change their status.

## New logo

Replace `logo.png` using GitHub's upload interface, keeping its filename. The next build optimizes it automatically. A new format/path requires updating `content/site.json`. The favicon is separate; replace `favicon.ico` at the same time. Header layout supports a square/compact mark; a wide new wordmark may need a small design adjustment.
