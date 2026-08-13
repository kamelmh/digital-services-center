import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app_instance import app, _sidebar


def social_scheduling_page():
    _sidebar()
    app.title("Social Media Content Scheduler")
    app.text("جدولة المحتوى — Social Media")

    with app.expander("📝 Add Post"):
        c1,c2 = app.columns(2)
        platform = c1.selectbox("Platform", ["LinkedIn","Instagram","Facebook","Twitter","TikTok"])
        post_type = c2.selectbox("Type", ["Image","Video","Carousel","Story","Text"])
        content = app.text_area("Content", placeholder="Write your post content...")
        c3,c4 = app.columns(2)
        date = c3.date_input("Schedule Date")
        time = c4.time_input("Schedule Time")
        if app.button("📅 Schedule Post", key="schedule_post"):
            if content.value:
                app.toast(f"Post scheduled for {date.value} at {time.value}", variant="success")
            else:
                app.warning("Please enter content")

    with app.expander("📅 Content Calendar"):
        app.info("No posts scheduled yet. Add your first post above!")

    with app.expander("📊 Best Posting Times"):
        app.markdown("""
        | Platform | Best Times (DZ) | Best Days |
        |----------|-----------------|-----------|
        | LinkedIn | 8-10am, 12-2pm | Tue-Thu |
        | Instagram | 11am-1pm, 7-9pm | Mon-Fri |
        | Facebook | 1-3pm, 7-9pm | Wed-Fri |
        | Twitter | 8-10am, 12-1pm | Tue-Wed |
        | TikTok | 7-9pm, 12-2pm | Tue-Thu |
        """)
