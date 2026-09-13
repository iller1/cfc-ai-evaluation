# HAWM + CFC Human Tester v0.1

A zero-install, browser-only public tester designed for people with no AI evaluation background.

## What the user does

1. Opens the page.
2. Reads 10 short situations.
3. Chooses what the AI is actually justified in saying.
4. Gets an immediate plain-language explanation.
5. Sees a simple score at the end.

No login, API, server, or database is required.

## Run locally

Open `index.html` in a browser.

## Put it on GitHub Pages

The simplest route:

1. Create a folder such as `docs/tester/` in the public repository.
2. Copy `index.html` there.
3. Enable GitHub Pages for the repository's `docs/` folder.
4. The tester will then be available at a URL similar to:

   `https://<username>.github.io/<repo>/tester/`

No backend is needed for v0.1.

## Feedback in v0.1

The tester does not collect any data.

At the end, the user can click **Copy my result** and paste the result into LinkedIn, email, a form, or a message.

A real feedback endpoint can be added later without changing the frozen CFC artifact.

## Method boundary

This is a human-understanding demonstrator, not a live execution of the frozen CFC controller.

Cases C09–C10 are adapted from the supplied HAWM Test R demonstrator.
Cases C01–C08 are synthetic teaching examples.

See `SOURCE_NOTE.md`.
