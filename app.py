"""여행 신청서 🧳 — 1박 2일 코스를 매력만 보고 골라 보는 핑크 & 하트 테마의 Streamlit 앱."""

from html import escape

import streamlit as st

from plans import CHECKLIST, HWADAM_NOTES, PLANS, TRIP

st.set_page_config(page_title="여행 신청서", page_icon="🧳", layout="centered")

# ---------------------------------------------------------------------------
# 코스 데이터 — 시간표 대신 '왜 끌리는지'만 담는다.
#   hook  : 코스 카드에 보이는 한 줄 매력
#   extra : 다른 코스를 골랐을 때 '한 번 더' 화면에서 어필하는 숨은 매력
#   night : 확인서에 들어가는 첫날 밤 한 줄
# ---------------------------------------------------------------------------
COURSES = {
    "A": {
        "emoji": "🏰",
        "name": "여주 루덴시아",
        "tag": "동화 속 유럽 마을",
        "hook": "유럽 동화 마을 골목을 걸으면서, 어디서 찍어도 인생샷 나오는 하루",
        "extra": "곳곳에 카페랑 전시가 숨어 있어서, 걷다가 쉬다가 느긋하게 데이트하기 딱 좋아 ☕",
        "night": "여주·이천 쪽 조용한 숙소에서 푹 쉬기",
    },
    "B": {
        "emoji": "🏯",
        "name": "용인 한국민속촌",
        "tag": "조선 시대로 시간여행",
        "hook": "조선 시대로 시간여행! 사또랑 장터 사람들한테 놀림받으며 하루 종일 웃다 오는 날",
        "extra": "해가 지면 등불 켜진 밤의 민속촌은 낮이랑 완전 딴 세상이야 🏮",
        "night": "용인·광주 쪽 숙소에서 오늘 웃긴 장면 다시 얘기하기",
    },
    "C": {
        "emoji": "🏺",
        "name": "이천 도자기 체험",
        "tag": "둘이 만드는 기념품",
        "hook": "둘이 같이 흙 만지면서 빚은 그릇, 여행이 끝나도 집에 남는 우리 기념품",
        "extra": "체험 끝나고 예스파크 공방 골목 구경하다가, 저녁은 따끈한 이천 쌀밥 한 상 🍚",
        "night": "이천·신둔 쪽 숙소에서 저녁 먹고 여유롭게 쉬기",
    },
}

DAY2 = "🌲 둘째 날은 셋 다 곤지암 화담숲 숲길 산책으로 마무리"

STEPS = ["신청", "코스", "완성"]

# ---------------------------------------------------------------------------
# 상태
# ---------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("step", 0)
ss.setdefault("course", None)  # "A" | "B" | "C"
ss.setdefault("switched", False)  # 확정한 뒤에 코스를 바꿨는지
ss.setdefault("scroll_id", 0)  # 확인서 화면 자동 스크롤을 한 번만 돌리기 위한 번호
ss.setdefault("scroll_mode", "tour")  # tour: 아래로 갔다가 3초 뒤 위로 / top: 바로 위로


def go(step: int) -> None:
    ss.step = step


def pick_course(key: str) -> None:
    ss.course = key
    ss.switched = False


def switch_course(key: str) -> None:
    """확정한 뒤 확인서 화면에서 다른 코스로 마음을 바꾼다. 화면은 그대로 두고 확인서만 바뀐다."""
    ss.course = key
    ss.switched = True
    ss.scroll_id += 1
    ss.scroll_mode = "top"  # 바뀐 확인서를 바로 보여 준다


def confirm() -> None:
    """확정: 확인서 화면으로 가서 아래 '이런 매력도 있는데'를 잠깐 보여 준다."""
    ss.scroll_id += 1
    ss.scroll_mode = "tour"
    go(2)


def restart() -> None:
    ss.course = None
    ss.switched = False
    ss.step = 0


# ---------------------------------------------------------------------------
# 전역 스타일: 핑크 테마 + 떠다니는 하트
# ---------------------------------------------------------------------------
st.html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Gaegu:wght@400;700&display=swap');

.stApp {
  background: linear-gradient(180deg, #fff0f6 0%, #ffe3ee 100%);
}
.stApp { color: #5b2140; }
.stApp, .stApp p, .stApp label, .stApp li {
  font-family: 'Gaegu', 'Jua', sans-serif;
  font-size: 1.15rem;
}
h1, h2, h3, .stButton button, .stDownloadButton button {
  font-family: 'Jua', sans-serif !important;
}
h1, h2, h3 { color: #e8457c !important; text-align: center; }
h1 { font-size: clamp(1.9rem, 8vw, 2.8rem) !important; white-space: nowrap; }

.stButton button, .stDownloadButton button {
  border-radius: 999px !important;
  border: 2px solid #ff8fb3 !important;
  transition: transform .15s ease;
}
.stButton button:hover, .stDownloadButton button:hover { transform: scale(1.05); }
.stButton button[kind="primary"] {
  background: linear-gradient(135deg, #ff6b9d, #ff4d88) !important;
  color: white !important;
  box-shadow: 0 6px 16px rgba(255, 77, 136, .35);
}

[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.75);
  border-radius: 24px !important;
}

.hearts { position: fixed; inset: 0; pointer-events: none; overflow: hidden; z-index: 0; }
.hearts span {
  position: absolute; bottom: -40px; opacity: .55;
  animation: floatUp linear infinite;
}
@keyframes floatUp {
  from { transform: translateY(0) rotate(0deg); }
  to   { transform: translateY(-115vh) rotate(25deg); }
}
.progress { text-align: center; font-size: 1.6rem; letter-spacing: .4rem; margin-bottom: .2rem; }
.progress-label { text-align: center; color: #c06088; font-size: 1rem; margin-bottom: 1rem; }
.stApp .subtitle { text-align: center; color: #b04a75; font-family: 'Jua', sans-serif; font-size: 1.6rem; }
.stApp .hint { text-align: center; color: #b04a75; font-size: 1.1rem; }
.course-emoji { text-align: center; font-size: 3rem; }
.course-name { text-align: center; font-family: 'Jua', sans-serif; color: #e8457c; font-size: 1.35rem; }
.course-tag { text-align: center; color: #c06088; font-size: .95rem; margin-bottom: .4rem; }
.stApp .course-line { text-align: center; font-family: 'Gaegu', sans-serif; font-size: 1.1rem; min-height: 7em; }
.course-day2 { text-align: center; color: #3f8f5a; font-size: .9rem; margin-bottom: .3rem; }
.plan-table { width: 100%; border-collapse: collapse; font-family: 'Gaegu', sans-serif; font-size: 1.05rem; }
.plan-table td { padding: .45rem .5rem; border-bottom: 1px dashed #ffc2d6; vertical-align: top; color: #5b2140; }
.plan-table td.t { white-space: nowrap; color: #e8457c; font-family: 'Jua', sans-serif; font-size: .95rem; width: 1%; }
.plan-table td.w { font-weight: 700; }
.plan-table td.d { color: #9a5a78; }
.plan-table tr.hl td { background: #e9f7ee; }
.plan-box { background: #fff7fa; border: 1px solid #ffd0e0; border-radius: 16px; padding: .7rem 1rem; margin: .6rem 0; color: #5b2140; }
.plan-box b { color: #e8457c; }
.plan-box ul { margin: .3rem 0 0; padding-left: 1.2rem; }
</style>
<div class="hearts">
  <span style="left:5%;  font-size:22px; animation-duration:11s; animation-delay:0s">💗</span>
  <span style="left:18%; font-size:16px; animation-duration:14s; animation-delay:3s">💕</span>
  <span style="left:32%; font-size:26px; animation-duration:12s; animation-delay:6s">💖</span>
  <span style="left:50%; font-size:18px; animation-duration:15s; animation-delay:1s">💓</span>
  <span style="left:66%; font-size:24px; animation-duration:13s; animation-delay:4s">💗</span>
  <span style="left:80%; font-size:16px; animation-duration:10s; animation-delay:7s">💞</span>
  <span style="left:92%; font-size:22px; animation-duration:16s; animation-delay:2s">💘</span>
</div>
"""
)



# ---------------------------------------------------------------------------
# 도망가는 거절 버튼 컴포넌트
# ---------------------------------------------------------------------------
ASK_HTML = """
<div class="arena">
  <button class="yes">좋아 💖</button>
  <button class="no">거절 🙅</button>
  <div class="tease"></div>
</div>
"""

ASK_CSS = """
.arena {
  position: relative; height: 260px; width: 100%;
  font-family: 'Jua', sans-serif; user-select: none;
}
button {
  position: absolute; top: 50%; transform: translate(-50%, -50%);
  border-radius: 999px; cursor: pointer; font-family: inherit;
  padding: .7em 1.6em; font-size: 1.3rem; white-space: nowrap;
}
.yes {
  left: 32%;
  background: linear-gradient(135deg, #ff6b9d, #ff4d88); color: #fff;
  border: none; box-shadow: 0 8px 20px rgba(255, 77, 136, .4);
  transition: font-size .25s ease;
  animation: beat 1.2s ease-in-out infinite;
  z-index: 2;
}
.yes:hover { filter: brightness(1.05); }
.no {
  left: 68%;
  background: #fff; color: #c06088; border: 2px solid #ffb3cc;
  transition: left .25s ease, top .25s ease;
  z-index: 1;
}
.tease {
  position: absolute; bottom: 0; width: 100%; text-align: center;
  color: #c06088; font-size: 1.05rem; min-height: 1.4em;
}
@media (max-width: 480px) {
  button { font-size: 1.1rem; padding: .6em 1.2em; }
  .yes { left: 27%; }
  .no { left: 74%; }
}
@keyframes beat {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50%      { transform: translate(-50%, -50%) scale(1.07); }
}
"""

ASK_JS = """
export default function (component) {
  const { parentElement, setTriggerValue } = component;
  const arena = parentElement.querySelector('.arena');
  const yes = parentElement.querySelector('.yes');
  const no = parentElement.querySelector('.no');
  const tease = parentElement.querySelector('.tease');

  const lines = [
    '어딜 누르려고~? 😏', '못 잡지롱 🏃‍♀️', '거절 버튼은 휴가 중이에요 🏖️',
    '그 버튼은 고장났어요 🔧', '좋아 버튼이 더 예쁜데? 💕', '포기하면 편해요 😚',
    '도망 성공! 🐰', '이쯤 되면 운명이야 💘',
  ];
  let escapes = 0;

  const runAway = (e) => {
    if (e) { e.preventDefault(); e.stopPropagation(); }
    const w = arena.clientWidth, h = arena.clientHeight;
    const bw = no.offsetWidth, bh = no.offsetHeight;
    const yr = yes.getBoundingClientRect(), ar = arena.getBoundingClientRect();
    const nr = no.getBoundingClientRect();
    const pt = e && e.touches ? e.touches[0] : e;
    // 커서(없으면 현재 버튼 위치)에서 멀리 도망간다
    const px = pt && pt.clientX != null ? pt.clientX - ar.left : nr.left - ar.left + nr.width / 2;
    const py = pt && pt.clientY != null ? pt.clientY - ar.top : nr.top - ar.top + nr.height / 2;
    const overlapsYes = (x, y) =>
      Math.abs(x - (yr.left - ar.left + yr.width / 2)) < (bw + yr.width) / 2 + 10 &&
      Math.abs(y - (yr.top - ar.top + yr.height / 2)) < (bh + yr.height) / 2 + 10;
    let x, y, tries = 0;
    do {
      x = bw / 2 + Math.random() * Math.max(1, w - bw);
      y = bh / 2 + Math.random() * Math.max(1, h - bh - 30);
      tries++;
    } while (tries < 60 && (overlapsYes(x, y) || Math.hypot(x - px, y - py) < Math.min(150, w / 3)));
    no.style.left = x + 'px';
    no.style.top = y + 'px';
    escapes++;
    tease.textContent = lines[(escapes - 1) % lines.length];
    yes.style.fontSize = Math.min(1.3 + escapes * 0.08, 2.4) + 'rem';
  };

  no.addEventListener('mouseenter', runAway);
  no.addEventListener('touchstart', runAway, { passive: false });
  no.addEventListener('focus', runAway);
  no.addEventListener('click', runAway);
  yes.addEventListener('click', () => setTriggerValue('answer', 'yes'));
}
"""

ask_component = st.components.v2.component(
    "trip_ask_buttons", html=ASK_HTML, css=ASK_CSS, js=ASK_JS
)


# ---------------------------------------------------------------------------
# 확인서 화면 자동 스크롤
#   tour: 확정 → 잠깐 뒤 아래 '이런 매력도 있는데'로 내려감 → 3초 동안 반응이 없으면 다시 확인서로 올라옴
#   top : 코스를 바꿨을 때 바뀐 확인서로 바로 올라옴
# 같은 번호(id)는 한 번만 실행한다. (화면이 다시 그려질 때마다 반복되지 않게)
# ---------------------------------------------------------------------------
SCROLL_JS = """
export default function (component) {
  const { data } = component;
  if (!data || !data.id || window.__tripScrollId === data.id) return;
  window.__tripScrollId = data.id;
  clearTimeout(window.__tripT1);
  clearTimeout(window.__tripT2);

  const go = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };
  if (data.mode === 'top') {
    window.__tripT1 = setTimeout(() => go('trip-top'), 300);
    return;
  }

  // 확정 화면을 잠깐 보여 준 뒤 아래로
  window.__tripT1 = setTimeout(() => {
    go('trip-others');
    // 사용자가 스크롤하거나 누르면 '반응한 것'으로 보고 위로 끌고 가지 않는다
    let answered = false;
    const events = ['wheel', 'touchstart', 'pointerdown', 'keydown'];
    const onAnswer = () => { answered = true; };
    events.forEach((ev) => window.addEventListener(ev, onAnswer, { passive: true }));
    // 내려가는 데 걸리는 시간(약 0.7초) + 3초
    window.__tripT2 = setTimeout(() => {
      events.forEach((ev) => window.removeEventListener(ev, onAnswer));
      if (!answered) go('trip-top');
    }, 3700);
  }, 1500);
}
"""

scroll_component = st.components.v2.component(
    "trip_auto_scroll", html="<span></span>", js=SCROLL_JS
)


def progress() -> None:
    hearts = "".join("💖" if i <= ss.step else "🤍" for i in range(len(STEPS)))
    st.html(
        f'<div class="progress">{hearts}</div>'
        f'<div class="progress-label">{ss.step + 1} / {len(STEPS)} · {STEPS[ss.step]}</div>'
    )


def course_card(key: str, *, line: str) -> None:
    c = COURSES[key]
    st.html(
        f'<div class="course-emoji">{c["emoji"]}</div>'
        f'<div class="course-name">{key}. {escape(c["name"])}</div>'
        f'<div class="course-tag">{escape(c["tag"])}</div>'
        f'<p class="course-line">{escape(line)}</p>'
        f'<div class="course-day2">🌲 다음 날은 화담숲</div>'
    )


# ---------------------------------------------------------------------------
# 페이지들
# ---------------------------------------------------------------------------
def page_ask() -> None:
    st.markdown("<h1>🧳 여행 신청서 🧳</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        st.html(
            '<div style="text-align:center;font-size:4rem">🥺👉👈</div>'
            '<p class="subtitle">저기... 나랑 1박 2일 여행 갈래?</p>'
        )
        result = ask_component(key="ask", on_answer_change=lambda: None)
    if result.answer == "yes":
        go(1)
        st.rerun()


def page_course() -> None:
    progress()
    st.markdown("## 🗺️ 첫날은 어디로 갈까?")
    st.html(f'<p class="hint">끌리는 대로 하나만 골라줘! 자세한 건 내가 다 알아볼게 😎</p>')
    cols = st.columns(3)
    for col, key in zip(cols, COURSES):
        with col.container(border=True):
            course_card(key, line=COURSES[key]["hook"])
            picked = ss.course == key
            st.button(
                "💖 선택됨" if picked else "여기 갈래!",
                key=f"course_{key}",
                on_click=pick_course,
                args=(key,),
                type="primary" if picked else "secondary",
                width="stretch",
            )
    st.html(f'<p class="hint">{DAY2}</p>')
    left, right = st.columns(2)
    left.button("← 이전", on_click=go, args=(0,), width="stretch")
    right.button("이걸로 결정! 💕", on_click=confirm, type="primary", disabled=not ss.course, width="stretch")


def other_courses() -> None:
    """확정한 뒤에 보여 주는 '근데 이런 매력도 있어' 카드. 누르면 확인서가 그 코스로 바뀐다."""
    st.html('<div id="trip-others" style="scroll-margin-top:4rem"></div>')
    st.markdown("### 🤔 근데 이런 매력도 있는데...")
    st.html('<p class="hint">확정은 했지만, 마음 바뀌면 지금 바꿔도 돼!</p>')
    others = [k for k in COURSES if k != ss.course]
    cols = st.columns(len(others))
    for col, key in zip(cols, others):
        with col.container(border=True):
            course_card(key, line=COURSES[key]["extra"])
            st.button(
                "오 이걸로 바꿀래!",
                key=f"switch_{key}",
                on_click=switch_course,
                args=(key,),
                width="stretch",
            )


def plan_text() -> str:
    c = COURSES[ss.course]
    lines = [
        "💖 여행 확인서 💖",
        "",
        f"☀️ {TRIP['day1']} : {c['emoji']} {ss.course}코스 · {c['name']} ({c['tag']})",
        f"   {c['hook']}",
        f"🌙 첫날 밤 : {c['night']}",
        f"🌲 {TRIP['day2']} : 느긋하게 일어나서 오후 2시에 곤지암 화담숲 산책",
        "",
        "숙소랑 길 찾기는 내가 알아서 할게 😎",
        "위 내용으로 여행을 약속합니다. 🤙 꼭 같이 가기!",
    ]
    return "\n".join(lines)


def detail_text() -> str:
    """저장용 세부 계획 (확인서 .txt 뒤에 붙인다)."""
    p = PLANS[ss.course]
    lines = ["", "", f"📋 세부 계획 · {ss.course}코스", p["concept"], "", f"[{TRIP['day1']}]"]
    lines += [f"{t}  {w}" + (f" ({d})" if d else "") for t, w, d in p["day1"]]
    lines += ["", "놓치지 말 것"] + [f"- {n}: {d}" for n, d in p["must"]]
    lines += ["", f"숙소: {p['stay'][0]} ({p['stay'][1]})", "", f"[{TRIP['day2']}]"]
    lines += [f"{t}  {w}" for t, w, _ in p["day2"]]
    lines += ["", "참고"] + [f"- {n}" for n in p["notes"] + HWADAM_NOTES]
    lines += ["", "떠나기 전에 확인"] + [f"- {n}" for n in CHECKLIST]
    return "\n".join(lines)


def schedule_table(rows: list[tuple[str, str, str]]) -> str:
    """시간표 HTML. 화담숲 입장 줄은 초록색으로 강조."""
    trs = []
    for t, w, d in rows:
        hl = ' class="hl"' if "화담숲 입장" in w else ""
        trs.append(
            f'<tr{hl}><td class="t">{escape(t)}</td><td class="w">{escape(w)}</td>'
            f'<td class="d">{escape(d)}</td></tr>'
        )
    return f'<table class="plan-table">{"".join(trs)}</table>'


def bullet_box(title: str, items: list[str]) -> str:
    lis = "".join(f"<li>{escape(x)}</li>" for x in items)
    return f'<div class="plan-box"><b>{escape(title)}</b><ul>{lis}</ul></div>'


def plan_details() -> None:
    """확인서 아래 '세부 계획': 고른 코스의 날짜별 시간표·숙소·확인할 것."""
    key = ss.course
    c, p = COURSES[key], PLANS[key]
    st.markdown(f"### 📋 세부 계획 · {c['emoji']} {key}코스")
    st.html(f'<p class="hint">{escape(TRIP["style"])}<br>{escape(p["concept"])}</p>')
    tab1, tab2, tab3 = st.tabs([f"☀️ {TRIP['day1']}", f"🌲 {TRIP['day2']}", "🏨 숙소·확인할 것"])
    with tab1:
        st.html(schedule_table(p["day1"]))
        st.html(bullet_box("✨ 놓치지 말 것", [f"{n} — {d}" for n, d in p["must"]]))
        st.html(bullet_box("💡 참고", p["notes"]))
    with tab2:
        st.html(schedule_table(p["day2"]))
        st.html(bullet_box("🌲 화담숲 주의할 점", HWADAM_NOTES))
    with tab3:
        area, why = p["stay"]
        st.html(f'<div class="plan-box"><b>🏨 숙소 권역</b><br>{escape(area)}<br>'
                f'<span style="color:#9a5a78">{escape(why)}</span></div>')
        st.html(bullet_box("✅ 떠나기 전에 확인", CHECKLIST))


def page_done() -> None:
    st.html('<div id="trip-top" style="scroll-margin-top:4rem"></div>')
    progress()
    if not ss.get("celebrated"):
        st.balloons()
        ss.celebrated = True
    st.markdown("<h1>🎉 여행 확정! 🎉</h1>", unsafe_allow_html=True)
    if ss.switched:
        st.html('<p class="hint">마음 바꾼 거 완전 좋아 🥰</p>')
    with st.container(border=True):
        st.html(f'<div style="text-align:center;font-size:3.5rem">{COURSES[ss.course]["emoji"]}💑🌲</div>')
        st.markdown(plan_text().replace("\n", "  \n"))
    st.download_button(
        "💾 확인서 저장하기",
        data=plan_text() + detail_text(),
        file_name="여행_확인서.txt",
        type="primary",
        width="stretch",
    )
    plan_details()
    other_courses()
    st.button("처음부터 다시", on_click=restart, width="stretch")
    scroll_component(data={"id": ss.scroll_id, "mode": ss.scroll_mode}, key="auto_scroll")


PAGES = [page_ask, page_course, page_done]
if ss.step > 1 and not ss.course:
    ss.step = 1
if ss.step != len(PAGES) - 1:
    ss.celebrated = False
PAGES[ss.step]()
