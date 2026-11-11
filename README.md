# Studio Notes – Roblox tutorial site

## Deploy
Drag this whole folder into https://app.netlify.com/drop

## Add a tutorial
Open `tutorials.json` and add a new object to the list (copy the Working Door example).
Fields: id (unique, no spaces), title, difficulty (Beginner / Intermediate / Advanced), tags,
description, youtube (video ID only, optional), steps, scripts, models, notes.

- In `code`, write line breaks as \n and quotes as \"
- A step can be text, or {"text": "...", "image": "images/step1.png"}
- Put images in an `images/` folder next to index.html

## Your links
Replace YOUR_INVITE, YOUR_CHANNEL and YOUR NAME in index.html.
