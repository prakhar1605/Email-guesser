"""
Founder Email Guesser
A small Streamlit tool to generate likely email permutations for cold outreach.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
import re

# ---------- Page config ----------
st.set_page_config(
    page_title="Founder Email Guesser",
    page_icon="📧",
    layout="centered",
)

st.title("📧 Founder Email Guesser")
st.caption("Generate likely email permutations for YC / startup cold outreach")

# ---------- Helpers ----------
def clean_name(name: str) -> str:
    """Lowercase + strip non-letters."""
    return re.sub(r"[^a-zA-Z]", "", name).lower()

def clean_domain(company: str) -> str:
    """Turn 'OpenAI' or 'open ai.com' into 'openai.com'."""
    company = company.strip().lower()
    # If user already gave a domain, keep it
    if "." in company:
        return re.sub(r"[^a-z0-9.\-]", "", company)
    # Otherwise strip spaces and add .com
    base = re.sub(r"[^a-z0-9]", "", company)
    return f"{base}.com"

def generate_emails(first: str, last: str, domain: str) -> list[dict]:
    """Generate ranked list of common email patterns."""
    f = clean_name(first)
    l = clean_name(last)

    if not f or not domain:
        return []

    fi = f[0] if f else ""
    li = l[0] if l else ""

    # Ordered by real-world frequency at startups (most common first)
    patterns = [
        ("first@",          f"{f}@{domain}",            "Most common at early-stage startups"),
        ("first.last@",     f"{f}.{l}@{domain}" if l else None,    "Very common at YC companies"),
        ("firstlast@",      f"{f}{l}@{domain}" if l else None,     "Common"),
        ("firstl@",         f"{f}{li}@{domain}" if l else None,    "Common at mid-size cos"),
        ("flast@",          f"{fi}{l}@{domain}" if l else None,    "Common"),
        ("first_last@",     f"{f}_{l}@{domain}" if l else None,    "Less common"),
        ("first-last@",     f"{f}-{l}@{domain}" if l else None,    "Less common"),
        ("f.last@",         f"{fi}.{l}@{domain}" if l else None,   "Occasional"),
        ("last@",           f"{l}@{domain}" if l else None,        "Occasional"),
        ("last.first@",     f"{l}.{f}@{domain}" if l else None,    "Rare"),
        ("hello@",          f"hello@{domain}",          "Generic — try as last resort"),
        ("founders@",       f"founders@{domain}",       "Generic — often read by founders"),
        ("team@",           f"team@{domain}",           "Generic"),
    ]

    return [
        {"Pattern": p, "Email": e, "Notes": n}
        for p, e, n in patterns
        if e is not None
    ]

def save_to_desktop(df: pd.DataFrame, founder: str, company: str) -> str | None:
    """Try to save CSV to user's Desktop. Returns filepath or None."""
    try:
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            # Some systems use OneDrive\Desktop on Windows
            alt = Path.home() / "OneDrive" / "Desktop"
            if alt.exists():
                desktop = alt
            else:
                return None

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", f"{founder}_{company}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = desktop / f"emails_{safe_name}_{timestamp}.csv"
        df.to_csv(filepath, index=False)
        return str(filepath)
    except Exception as e:
        st.error(f"Couldn't save to desktop: {e}")
        return None

# ---------- Input form ----------
with st.form("email_form"):
    col1, col2 = st.columns(2)
    with col1:
        founder_name = st.text_input(
            "Founder name",
            placeholder="e.g. Paul Graham",
            help="First and last name. Middle names are ignored.",
        )
    with col2:
        company_input = st.text_input(
            "Company name or domain",
            placeholder="e.g. ycombinator.com or OpenAI",
            help="Either a domain (stripe.com) or company name (will append .com)",
        )

    submitted = st.form_submit_button("🔍 Generate emails", use_container_width=True)

# ---------- Output ----------
if submitted:
    if not founder_name or not company_input:
        st.warning("Please enter both a founder name and a company.")
    else:
        # Parse name
        parts = founder_name.strip().split()
        if len(parts) < 1:
            st.warning("Enter at least a first name.")
            st.stop()

        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        domain = clean_domain(company_input)

        st.success(f"Generated emails for **{first} {last}** at **{domain}**")

        emails = generate_emails(first, last, domain)
        df = pd.DataFrame(emails)

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Save options
        st.subheader("💾 Save")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Save to Desktop", use_container_width=True):
                path = save_to_desktop(df, f"{first}_{last}", domain.split(".")[0])
                if path:
                    st.success(f"Saved to: `{path}`")
                else:
                    st.warning("Couldn't access Desktop (likely running on cloud). Use Download instead.")

        with col_b:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"emails_{first}_{last}_{domain.split('.')[0]}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        # Verification tip
        with st.expander("💡 How to verify which one is real"):
            st.markdown(
                """
                Free tools to check which guess actually exists:
                - **[Hunter.io](https://hunter.io)** — free 25 verifications/month, also finds emails by domain
                - **[NeverBounce](https://neverbounce.com)** — verifies if an inbox exists
                - **[Apollo.io](https://apollo.io)** — free tier gives you verified founder emails directly
                - **Gmail trick** — compose a draft to all guesses; Gmail often shows a profile picture next to the real one

                **Pro tip for cold outreach:** start with `first@domain.com` — at 70%+ of YC seed-stage
                companies the founder owns this address.
                """
            )