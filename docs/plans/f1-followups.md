# F1 parser follow-ups

- **Mixed input:** `vercel/next.js zustand` should raise `InvalidRepoInput("Enter up to 3 repositories, or one search, not both")`. It currently crashes with an unhandled `ValueError`.
- **Incomplete links:** `https://github.com/vercel` and `https://gitlab.com` currently crash with an unhandled `ValueError`. They need a decided behavior and a test.
- **"state management" guard:** `state management` already returns `search="state management"`, but no test pins it. Add a guard test so plain words stay one search and never hit the 3-repository limit.
