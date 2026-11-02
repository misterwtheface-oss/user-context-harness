# House rules for Claude (set up {{DATE}} by the user-context-harness skill)

My Claude work lives in one place:

```
{{HOME}}
```

In words: {{HOME_CLICK_PATH}}.

- When I name a project, open its `CONTEXT.md` and then its `PROGRESS.md` inside `{{HOME}}/projects/` before doing
  anything else. The project folders and the phrases I use for them are listed in the README there.
- Work where the project's `CONTEXT.md` says its files live (a repo, a shared folder). Anything new that has no such
  place goes in that project's `files/` folder, never in Downloads, Desktop, or wherever Claude Code happened to start. If no project fits, put it in `{{HOME}}/inbox/` and tell me.
- Whenever you save or move a file, tell me where it is in plain words (which folders to click through), and give the
  full path too.
- Never move, rename, or delete a file I already had without first showing me a list of exactly what would move and
  where, and waiting for my yes. Log every approved move in `{{HOME}}/inbox/MOVED.md`.
- Before the session ends, update the project's `PROGRESS.md`: where things stand, what you are waiting on me for, what is
  still open, and one line in the session log.
- Talk to me in plain language. If you use a technical word, explain it in the same sentence.
- Name new files date first: `YYYY-MM-DD short description.ext`.
