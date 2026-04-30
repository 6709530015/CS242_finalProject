from models.event_manager import EventManager
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import io
import base64
from database import get_all_events

# โหลด font ไทย (THSarabunNew หรือ fallback)
def _get_thai_font():
    thai_fonts = [
        "THSarabunNew", "TH Sarabun New", "Tahoma",
        "Microsoft Sans Serif", "Arial Unicode MS"
    ]
    for name in thai_fonts:
        try:
            fp = fm.findfont(fm.FontProperties(family=name), fallback_to_default=False)
            if fp:
                return fm.FontProperties(family=name)
        except Exception:
            continue
    return fm.FontProperties()  # default

THAI_FONT = _get_thai_font()

class ReminderSystem:
    def __init__(self, manager: EventManager):
        self._manager = manager
        
    def _get_df(self):
        """ดึงข้อมูลจาก SQLite แล้วแปลงเป็น DataFrame"""
        rows = get_all_events()
        # tuple: (id, title, date, subject, description, priority, status, calendar_id)
        df = pd.DataFrame(rows, columns=[
            "id", "title", "date", "subject",
            "description", "priority", "status", "calendar_id"
        ])
        if df.empty:
            return df
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.strftime("%b %Y")
        df["month_num"] = df["date"].dt.to_period("M")
        return df


    def send_reminder(self):
        """คืน list ของ event ที่กำลังจะถึง (status = TODAY หรือ UPCOMING ≤ 3 วัน)"""
        from datetime import datetime
        rows = get_all_events()
        reminders = []
        today = datetime.now().date()
        for row in rows:
            # row: (id, title, date, subject, description, priority, status)
            try:
                event_date = datetime.strptime(row[2], "%Y-%m-%d").date()
                days_left = (event_date - today).days
                if 0 <= days_left <= 3:
                    reminders.append({
                        "title": row[1],
                        "date": row[2],
                        "subject": row[3],
                        "priority": row[5],
                        "days_left": days_left,
                        "status": "TODAY" if days_left == 0 else "UPCOMING"
                    })
            except Exception:
                continue
        return reminders

    def analyze_events(self):
        """วิเคราะห์สถิติด้วย Pandas"""
        df = self._get_df()
        if df.empty:
            return {}

        return {
            "total": len(df),
            "by_subject": df["subject"].value_counts().to_dict(),
            "by_priority": df["priority"].value_counts().to_dict(),
            "by_month": df.groupby("month").size().to_dict(),
            "by_status": df["status"].value_counts().to_dict(),
            "overdue": int((df["status"] == "OVERDUE").sum()),
            "upcoming": int((df["status"] == "UPCOMING").sum()),
            "today": int((df["status"] == "TODAY").sum()),
        }

    def generate_calendar_view(self):
        """สร้างกราฟ 2 แบบ คืนเป็น base64 PNG"""
        df = self._get_df()
        if df.empty:
            return None

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
        fig.patch.set_facecolor('#0f0f0f')

        # --- กราฟ 1: จำนวนนัดหมายต่อเดือน ---
        ax1 = axes[0]
        ax1.set_facecolor('#1a1a1a')
        monthly = df.groupby("month_num").size().reset_index(name="count")
        monthly["label"] = monthly["month_num"].dt.strftime("%b %Y")
        bars = ax1.bar(
            monthly["label"], monthly["count"],
            color='#4f8ef7', edgecolor='none', width=0.6
        )
        # ใส่ตัวเลขบน bar
        for bar in bars:
            h = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2, h + 0.05,
                str(int(h)), ha='center', va='bottom',
                color='white', fontsize=10, fontweight='bold'
            )
        ax1.set_title("จำนวนนัดหมายต่อเดือน", color='white', fontsize=20,
                      pad=12, fontproperties=THAI_FONT)
        ax1.set_xlabel("เดือน", color='#aaaaaa', fontsize=20,
                       fontproperties=THAI_FONT)
        ax1.set_ylabel("จำนวน", color='#aaaaaa', fontsize=20,
                       fontproperties=THAI_FONT)
        ax1.tick_params(colors='#aaaaaa', labelsize=9)
        ax1.spines[:].set_color('#333333')
        ax1.set_ylim(0, monthly["count"].max() + 1.5 if not monthly.empty else 5)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')

        # --- กราฟ 2: สัดส่วนความสำคัญ ---
        ax2 = axes[1]
        ax2.set_facecolor('#1a1a1a')
        priority_counts = df["priority"].value_counts()
        priority_thai = {
            "LOW": "ต่ำ",
            "MEDIUM": "ปานกลาง",
            "HIGH": "สูง",
            "URGENT": "เร่งด่วน"
        }
        color_map = {
            "LOW": "#4CAF50",
            "MEDIUM": "#FFC107",
            "HIGH": "#FF9800",
            "URGENT": "#F44336"
        }
        pie_colors = [color_map.get(p, "#888888") for p in priority_counts.index]
        wedges, texts, autotexts = ax2.pie(
            priority_counts.values,
            labels=None,
            colors=pie_colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.75,
            wedgeprops=dict(edgecolor='#0f0f0f', linewidth=2)
        )
        for at in autotexts:
            at.set_color('white')
            at.set_fontsize(9)
        legend_patches = [
            mpatches.Patch(
                color=color_map.get(p, "#888"),
                label=priority_thai.get(p, p)
            )
            for p in priority_counts.index
        ]
        ax2.legend(
            handles=legend_patches, loc="lower center",
            bbox_to_anchor=(0.5, -0.18), ncol=2,
            frameon=False, labelcolor='white', fontsize=9,
            prop=THAI_FONT
        )
        ax2.set_title("สัดส่วนความสำคัญ", color='white', fontsize=13,
                      pad=12, fontproperties=THAI_FONT)

        plt.tight_layout(pad=2.5)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight',
                    facecolor="#333333", dpi=130)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img_b64