# Lumio X Auto-Posting (Buffer + GitHub Actions)

This is a free-tier-friendly workflow for the Lumio X account @lumiolearn. It **does not use the paid X API**.

## Complete setup

1. Connect your X account @lumiolearn to your Buffer account.
2. Verify your email and create a personal Buffer API key at https://publish.buffer.com/settings/api. Give it read and post permissions.
3. Open GitHub repository Settings > Secrets and variables > Actions > Secrets > New repository secret.
4. Create a repository secret **BUFFER_API_KEY** with the copied key. Do not share the key in chat or put it in a public file.
5. If you have more than one X account connected in Buffer, create an Actions **variable** BUFFER_CHANNEL_ID containing the Buffer channel ID for @lumiolearn. For one X account this is optional.
6. Open Actions > Lumio X Autopost via Buffer > Run workflow and check the logs. Enable Actions if the repository is inactive/disabled.

## Schedule and limits

- GitHub Actions runs at **05:47 IST** every day (00:17 UTC).
- The script schedules posts in Buffer for **09:00, 14:00, and 19:00 IST**.
- It checks existing scheduled Buffer posts and only uses the available Free queue capacity (max 10 queued per channel). It does not overwrite existing slot bookings.
- 45 original posts are included: 15 days starting **23 October 2026**, ending **6 November 2026**.
- Extend the content bank by appending three unique posts for each additional day to lumio-autopost/posts.json. Posts stop automatically when the bank is exhausted; they are not recycled.
- To inspect upcoming text without contacting Buffer, run: python lumio-autopost/publish.py --dry-run
- To stop automatic scheduling, disable the workflow in the Actions tab or remove the BUFFER_API_KEY secret. Previously scheduled posts remain in Buffer until removed there.

## Safety / troubleshooting

- Review the initial Buffer queue before letting publishing proceed. Scheduled events can be delayed by GitHub.
- If the workflow says it cannot select one X channel, set BUFFER_CHANNEL_ID under Actions variables; make sure X channel is not paused.
- Buffer API keys expire. Renew the repository secret before the key expires.
- Never paste the Buffer key into an issue, pull request, commit, or chat.
- This repository uses the public Free Actions entitlement; the secret is available only to approved workflows on the main branch, after you merge the pull request.

## Official docs

- https://developers.buffer.com/guides/getting-started.html
- https://developers.buffer.com/guides/data-model.html
- https://developers.buffer.com/guides/posts-and-scheduling.html
- https://developers.buffer.com/examples/get-scheduled-posts.html
- https://buffer.com/pricing
