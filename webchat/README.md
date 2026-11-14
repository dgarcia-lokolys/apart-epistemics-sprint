# Web-chat packet

Paste-ready instructions and batches for running the 55 frozen ClaimStanceBench items by hand in the free web chats of ChatGPT, Gemini, and Claude. The main set is six pastes per service (batches of 10, 10, 10, 10, 10, and 5) using the default harness prompt. An optional second set of six pastes uses the same item order and the permissive prompt wording. The item order is a fixed shuffle (seed 20261113). All 17 pair twins are in different batches.

Use `webchat-instructions-and-batches.md` as the copy source. Blank reply templates for the main set and the optional permissive set are in this folder. When a template is filled, score it with no API calls:

```
python -m harness.score_webchat --template path/to/filled-template.md --service chatgpt
```

For a filled permissive template, add `--variant permissive` and point at `reply-template-<service>-permissive.md`. Replace `chatgpt` with `gemini` or `claude` as needed. Scores use the same binary, three-way, and partial-pass hooks as the API runs, labeled as the separate conditions "consumer web chat, batched x10" and "consumer web chat, batched x10, permissive".
