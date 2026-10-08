import os
from datetime import datetime, timedelta, timezone

# Zimbabwe does not observe daylight saving, so a fixed offset avoids a tzdata dependency on hosts.
CAT = timezone(timedelta(hours=2), name="CAT")


class Config:
    SITE_NAME = "Opportunity Circle"
    SITE_TAGLINE = "Be part of the solution"
    SITE_DESCRIPTION = (
        "Opportunity Circle is a team of six Zimbabweans part of the 2026 Innovation Challenge organized by Education Matters and Kutunga."
    )
    SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")

    # 11 Dec 2026 is the last day. The clock reaches zero at midnight as 12 Dec begins.
    LAUNCH_DAY = datetime(2026, 12, 11, tzinfo=CAT)
    LAUNCH_LABEL = "11 Dec 2026"
    COUNTDOWN_END = datetime(2026, 12, 12, tzinfo=CAT)
    CONTACT_EMAIL = "contact@opportunitycircle.info"

    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=365)
