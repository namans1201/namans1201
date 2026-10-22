# Profile assets

Edit the root `README.md` directly. There is no README generator and no runtime stats-card service.

- `workbench.svg` and `workbench-compact.svg` (narrow screens): self-contained header artwork. Edit its SVG text, paths, and colours directly.
- `naman-intro.gif`: the original, unmodified animation copied from `Namans12/Namans12/assets/naman-intro.gif`. Kept here so the profile does not depend on the other repository's branch or asset path.
- The contribution snake is published to the `output` branch by `.github/workflows/snake.yml`. It refreshes twice daily and can be run manually in Actions. The job declares `contents: write` and uses the built-in `GITHUB_TOKEN`; no personal access token or Vercel deployment is required. If generation fails, the last published images remain available.

Project descriptions and milestones are static text. Update them here when the work changes; project links always lead to their source repositories.
