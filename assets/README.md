# Profile artwork and statistics

Edit the root `README.md` directly. The active design is Compact; `designs/editorial/` preserves the separate Editorial concept for @Namans12.

- `naman-intro.gif` is the unmodified original animation, copied from `Namans12/Namans12/assets/naman-intro.gif`.
- `intro-title-*.svg` renders the greeting without GitHub’s heading rule crossing the animation.
- `buttons/` and `projects/` contain self-contained SVGs, including light, dark, and narrow-screen variants. Run `python3 scripts/make_profile_assets.py` from the repository root to rebuild them and the saved Editorial assets. The script does not overwrite either README.
- `generated/` holds the last successful contribution cards and aggregate `stats.json`. Generate with `python3 scripts/profile_stats.py` using an authenticated `gh` CLI. No third-party renderer or Vercel instance is involved.
- `.github/workflows/profile-stats.yml` refreshes the cards every six hours, commits only `assets/generated/`, and does not trigger itself. It uses the built-in `GITHUB_TOKEN` and declares `contents: write`. Branch rules must allow that workflow's updates. Failed data retrieval leaves the published cards untouched. Initial snapshots are committed with the design so cards exist before the first scheduled run.
- The snake has its own existing `.github/workflows/snake.yml`, which publishes to the `output` branch twice daily. It remains independent of the stats cards.

## What the numbers mean

The script fetches every calendar year from the account's creation date, combines daily contribution counts, and calculates streaks across year boundaries. Total contributions means the lifetime sum returned by GitHub's contribution calendar, not only the last year, and is not a commit count. Visibility follows GitHub and the API token's permissions; a repository workflow token does not grant access to unrelated private repositories. Only aggregate metrics and date ranges are saved.

A streak requires at least one contribution per consecutive calendar day. Current streak includes today if active; otherwise it may end yesterday, allowing an unfinished day to continue. Longest streak is calculated over the full retrieved history. Card timestamps and the current-day boundary use Asia/Kolkata; the contribution dates themselves are the dates returned by GitHub. The card is a periodically refreshed snapshot, not a live counter. GitHub may delay attribution of new contributions.

References: [GitHub contribution calendar schema](https://docs.github.com/en/graphql/reference/users#contributioncalendar), [contribution counting](https://docs.github.com/en/account-and-profile/how-tos/setting-up-and-managing-your-github-profile/managing-contribution-settings-on-your-profile/viewing-contributions-on-your-profile), and the [usual streak definitions](https://github.com/DenverCoder1/github-readme-streak-stats#how-these-stats-are-calculated).
