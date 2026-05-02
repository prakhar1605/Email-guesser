# 📧 Founder Email Guesser

A small Streamlit tool that generates likely email permutations for cold outreach to founders at YC / early-stage startups.

## What it does

Enter a founder's name and company → get a ranked list of probable email addresses (e.g. `paul@ycombinator.com`, `paul.graham@ycombinator.com`, etc.) → save to your Desktop or download as CSV.

## Quick start (run locally — Desktop save works)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Run
streamlit run email_guesser.py
```

The app will open at `http://localhost:8501`. The "Save to Desktop" button works when running locally.

## Deploy to Streamlit Cloud (free)

1. Push these files to a GitHub repo:
   - `email_guesser.py`
   - `requirements.txt`

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click **"New app"** → connect your GitHub repo → set main file to `email_guesser.py` → **Deploy**.

You'll get a public URL in ~2 minutes. On the cloud version, "Save to Desktop" won't work (cloud servers can't write to your local machine) — use the **Download CSV** button instead.

## Tips for using the output

1. Start cold outreach with `first@company.com` — at 70%+ of YC seed-stage companies the founder owns this.
2. To verify which guess is real, paste them into [Hunter.io](https://hunter.io) (25 free/month) or compose a Gmail draft — the real one usually shows a profile picture.
3. For batch verification, [Apollo.io](https://apollo.io) gives you verified founder emails directly on the free tier.