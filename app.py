import streamlit as st
import re
from math import floor
from prompts import build_system_prompt, build_recipe_prompt
from gpt import ask_yandex_gpt
from storage import save_profile, load_profile, delete_profile, save_recipe, load_history, clear_history, \
    get_weekly_stats
from rag import search_recipe, format_rag_context
from nutrition import check_allergens

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  

st.set_page_config(
    page_title="SmartDiet - персональный нутрициолог",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(
        180deg,
        #f5f3ff 0%,
        #f8fafc 40%,
        #ffffff 100%
    );
    color: #111827;
}


.main::before {
    content: "";
    position: fixed;
    width: 500px;
    height: 500px;
    background: rgba(139, 92, 246, 0.18);
    filter: blur(120px);
    top: -100px;
    right: -100px;
    z-index: -1;
}

.main::after {
    content: "";
    position: fixed;
    width: 400px;
    height: 400px;
    background: rgba(168, 85, 247, 0.12);
    filter: blur(120px);
    bottom: -100px;
    left: -100px;
    z-index: -1;
}


.block-container {
    padding-top: 2rem;
    max-width: 1050px;
}


[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.5);
}


.glass-card {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.5);
    border-radius: 28px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow:
        0 8px 32px rgba(139,92,246,0.08),
        0 2px 8px rgba(0,0,0,0.04);
}


.main-title {
    font-size: 64px;
    font-weight: 700;
    letter-spacing: -3px;
    line-height: 1.2;
    margin-bottom: 12px;
    color: #ffffff;
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #7c3aed
    );
    padding: 20px 32px;
    border-radius: 28px;
    display: inline-block;
    box-shadow:
        0 8px 32px rgba(124, 58, 237, 0.25);
}

.subtitle {
    font-size: 22px;
    color: #6b7280;
    margin-bottom: 30px;
}


.stTextArea textarea,
.stTextInput input {
    background: rgba(255,255,255,0.75) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(139,92,246,0.15) !important;
    border-radius: 24px !important;
    padding: 18px !important;
    color: #111827 !important;
    font-size: 16px !important;
    transition: 0.25s ease;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border: 1px solid #8b5cf6 !important;
    box-shadow:
        0 0 0 4px rgba(139,92,246,0.12),
        0 8px 24px rgba(139,92,246,0.14) !important;
}


.stButton button {
    height: 58px;
    border-radius: 20px;
    border: none;
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #7c3aed
    );
    color: white;
    font-size: 16px;
    font-weight: 600;
    box-shadow:
        0 8px 24px rgba(124,58,237,0.28);
    transition: 0.25s ease;
}

.stButton button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow:
        0 12px 32px rgba(124,58,237,0.35);
}



.ai-glow {
    position: relative;
}

.ai-glow::before {
    content: "";
    position: absolute;
    inset: -2px;
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #a855f7,
        #c084fc
    );
    border-radius: 30px;
    z-index: -1;
    filter: blur(18px);
    opacity: 0.5;
}



.chat-bubble {
    background: rgba(255,255,255,0.78);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.6);
    border-radius: 28px;
    padding: 24px;
    margin-top: 20px;
    box-shadow:
        0 8px 24px rgba(0,0,0,0.05);
    animation: fadeUp 0.4s ease;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}



.typing {
    display: flex;
    gap: 6px;
    align-items: center;
    padding: 12px 0;
}

.typing span {
    width: 10px;
    height: 10px;
    background: #8b5cf6;
    border-radius: 50%;
    animation: bounce 1.3s infinite;
}

.typing span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes bounce {
    0%, 80%, 100% {
        transform: scale(0.7);
        opacity: 0.5;
    }
    40% {
        transform: scale(1.2);
        opacity: 1;
    }
}



.stMetric {
    background: rgba(255,255,255,0.72);
    backdrop-filter: blur(18px);
    border-radius: 24px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.5);
    box-shadow:
        0 8px 24px rgba(0,0,0,0.04);
}



button[kind="segmented_control"] {
    border-radius: 18px !important;
}



.stChatInputContainer {
    position: sticky;
    bottom: 20px;
}

.stFormSubmitButton button {
    height: 58px;
    border-radius: 20px;
    border: none;
    background: linear-gradient(
        135deg,
        #8b5cf6,
        #7c3aed
    );
    color: white;
    font-size: 16px;
    font-weight: 600;
    box-shadow:
        0 8px 24px rgba(124,58,237,0.28);
    transition: 0.25s ease;
}

.stFormSubmitButton button:hover {
    transform: translateY(-2px);
}
.glass-card {
    animation: floatCard 0.5s ease;
}

@keyframes floatCard {
    from {
        opacity:0;
        transform:translateY(20px);
    }
    to {
        opacity:1;
        transform:translateY(0);
    }
}
.stCheckbox {
    background: rgba(255,255,255,0.55);
    padding: 10px 14px;
    border-radius: 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(139,92,246,0.08);
}

.stRadio > div {
    background: rgba(255,255,255,0.55);
    padding: 14px;
    border-radius: 18px;
}



header {
    background: transparent !important;
}

footer {
    visibility: hidden;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: rgba(139,92,246,0.3);
    border-radius: 20px;
}

.weekly-stats {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(18px);
    border-radius: 20px;
    padding: 20px;
    margin-top: 15px;
    border: 1px solid rgba(139,92,246,0.12);
}

</style>
""", unsafe_allow_html=True)


def calculate_calories(weight, height, age, gender, goal):
    if gender == "Мужской":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    bmr *= 1.375

    multipliers = {
        "Похудение": 0.80,
        "Поддержание веса": 1.00,
        "Набор мышечной массы": 1.20,
    }
    return floor(bmr * multipliers.get(goal, 1.0))


def extract_kbju_from_text(text: str) -> dict:

    kbju = {}
    patterns = {
        "calories": [
            r'\|\s*Калории[^|]*\|\s*(\d+)\s*ккал',
            r'Калории[^\d]*(\d+)',
        ],
        "proteins": [
            r'\|\s*Белки[^|]*\|\s*(\d+)\s*г',
            r'Белки[^\d]*(\d+)',
        ],
        "fats": [
            r'\|\s*Жиры[^|]*\|\s*(\d+)\s*г',
            r'Жиры[^\d]*(\d+)',
        ],
        "carbs": [
            r'\|\s*Углеводы[^|]*\|\s*(\d+)\s*г',
            r'Углеводы[^\d]*(\d+)',
        ],
    }

    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text)
            if match:
                kbju[key] = int(match.group(1))
                break

    return kbju


def show_profile_form():
    st.markdown("""
    <div class="ai-glow glass-card">

    <div class="main-title">
    SmartDiet
    </div>

    <div class="subtitle">
    AI-нутрициолог с учётом вашего здоровья
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="
    display:flex;
    align-items:center;
    gap:12px;
    margin-bottom:20px;
    ">

    <div style="
    background:linear-gradient(135deg,#8b5cf6,#7c3aed);
    width:42px;
    height:42px;
    border-radius:14px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-weight:700;
    font-size:18px;
    box-shadow:0 8px 24px rgba(124,58,237,0.25);
    ">
    1
    </div>

    <div>
    <div style="
    font-size:20px;
    font-weight:600;
    color: var(--text-color);
    ">
    Медицинский профиль
    </div>

    <div style="
    font-size:14px;
    color:#6b7280;
    ">
    AI будет учитывать ваше здоровье при каждом рецепте
    </div>
    </div>

    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form"):

        st.markdown("#### 👤 Основные данные")
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Возраст", min_value=10, max_value=100, value=30)
        with col2:
            weight = st.number_input("Вес (кг)", min_value=30, max_value=250, value=70)
        with col3:
            height = st.number_input("Рост (см)", min_value=100, max_value=230, value=170)

        gender = st.radio("Пол", ["Мужской", "Женский"], horizontal=True)

        goal = st.selectbox(
            "Цель питания",
            ["Похудение", "Поддержание веса", "Набор мышечной массы"],
        )

        st.markdown("#### Заболевания и ограничения")
        st.caption("Выберите всё, что относится к вам")

        col_a, col_b = st.columns(2)
        with col_a:
            cond_diabetes = st.checkbox("🩸 Сахарный диабет 2 типа")
            cond_hyper = st.checkbox("❤️ Гипертония")
            cond_gastrit = st.checkbox("🫁 Гастрит / язва")
        with col_b:
            cond_lactose = st.checkbox("🥛 Непереносимость лактозы")
            cond_gluten = st.checkbox("🌾 Целиакия (без глютена)")
            cond_gout = st.checkbox("🦵 Подагра")

        allergies = st.text_input(
            "⚠️ Аллергии (перечислите через запятую)",
            placeholder="Например: орехи, морепродукты, мёд...",
        )

        submitted = st.form_submit_button(
            "Сохранить профиль и продолжить →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        calories = calculate_calories(weight, height, age, gender, goal)

        conditions = []
        if cond_diabetes: conditions.append("Сахарный диабет 2 типа")
        if cond_hyper:    conditions.append("Гипертония")
        if cond_gastrit:  conditions.append("Гастрит / язва")
        if cond_lactose:  conditions.append("Непереносимость лактозы")
        if cond_gluten:   conditions.append("Целиакия (без глютена)")
        if cond_gout:     conditions.append("Подагра")

        st.session_state.profile = {
            "age": age,
            "weight": weight,
            "height": height,
            "gender": gender,
            "goal": goal,
            "calories": calories,
            "conditions": conditions,
            "allergies": allergies.strip(),
        }
        save_profile(st.session_state.profile)
        st.rerun()


def show_main_screen():
    profile = st.session_state.profile

    with st.sidebar:
        st.markdown("### 👤 Ваш медпрофиль")
        st.metric("Норма калорий", f"{profile['calories']} ккал/день")

        goal_short = profile["goal"].split(" ")[0]
        st.metric("Цель", goal_short)

        if profile["conditions"]:
            st.markdown("**🩺 Учитываю заболевания:**")
            for c in profile["conditions"]:
                st.markdown(f"- {c}")
        else:
            st.success("Нет ограничений по здоровью")

        if profile["allergies"]:
            st.error(f"⚠️ Аллергии:\n{profile['allergies']}")

        st.divider()
        if st.button("✏️ Изменить профиль", use_container_width=True):
            delete_profile()
            if "history" in st.session_state:
                del st.session_state.history
            del st.session_state.profile
            st.rerun()

    st.markdown("""
    <div class="ai-glow glass-card">

    <div class="main-title">
    SmartDiet
    </div>

    <div class="subtitle">
    AI-нутрициолог с учётом вашего здоровья
    </div>

    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("""
    <div class="glass-card">
    <h2>Что есть в холодильнике?</h2>
    <p style="color:#6b7280;">
    Перечислите продукты через запятую
    </p>
    </div>
    """, unsafe_allow_html=True)

    ingredients = st.text_area(
        "Перечислите продукты через запятую",
        placeholder=(
            "Например: куриное филе, брокколи, творог 5%, яйца, "
            "помидоры, оливковое масло, гречка..."
        ),
        height=90,
        label_visibility="collapsed",
    )

    meal_type = st.segmented_control(
        "🍽 Приём пищи",
        options=["🌅 Завтрак", "☀️ Обед", "🌙 Ужин", "🍎 Перекус"],
        default="☀️ Обед",
    )

    generate_btn = st.button(
        "🔍 Подобрать рецепт под мой профиль",
        type="primary",
        use_container_width=True,
    )

    if generate_btn:
        if not ingredients.strip():
            st.warning("⚠️ Введите хотя бы несколько продуктов")
        else:

            safe_meal_type = meal_type if meal_type else "☀️ Обед"

            st.divider()
            st.markdown("### 🤖 Ваш персональный рецепт")


            user_ingredients_list = [i.strip().lower() for i in ingredients.split(",") if i.strip()]
            allergens_found = check_allergens(user_ingredients_list, profile.get("allergies", ""))

            if allergens_found:
                st.error(f"⚠️ Обнаружены аллергены в ваших продуктах: {', '.join(allergens_found)}")
                st.stop()


            rag_result = search_recipe(
                ingredients=user_ingredients_list,
                profile=profile,
                meal_type=safe_meal_type,
            )

            system  = build_system_prompt(profile)
            user_msg = build_recipe_prompt(ingredients, safe_meal_type)

            if rag_result:
                user_msg += "\n\n" + format_rag_context(rag_result)
                st.info(f"📚 Найден подходящий рецепт в базе знаний: **{rag_result['name']}**")


            typing_placeholder = st.empty()
            typing_placeholder.markdown("""
            <div class="typing">
            <span></span><span></span><span></span>
            </div>
            """, unsafe_allow_html=True)


            full_result = ""
            result_placeholder = st.empty()

            for chunk in ask_yandex_gpt(system, user_msg):
                full_result += chunk
                result_placeholder.markdown(
                    f'<div class="chat-bubble">{full_result}▌</div>',
                    unsafe_allow_html=True,
                )


            typing_placeholder.empty()
            result_placeholder.markdown(
                f'<div class="chat-bubble">{full_result}</div>',
                unsafe_allow_html=True,
            )


            kbju = extract_kbju_from_text(full_result)
            save_recipe(
                meal_type=safe_meal_type,
                ingredients=ingredients,
                recipe_text=full_result,
                kbju=kbju,
            )

            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({
                "meal_type":   safe_meal_type,
                "ingredients": ingredients,
                "recipe":      full_result,
            })

            if kbju and kbju.get("calories"):
                st.success(
                    f"✅ Сохранено: {kbju['calories']} ккал | "
                    f"Б {kbju.get('proteins', '?')}г | "
                    f"Ж {kbju.get('fats', '?')}г | "
                    f"У {kbju.get('carbs', '?')}г"
                )


    if st.session_state.get("history"):
        st.divider()
        with st.expander(f"📚 История рецептов ({len(st.session_state.history)} шт.)"):
            for i, item in enumerate(reversed(st.session_state.history[:-1]), 1):
                st.markdown(f"**{i}. {item['meal_type']}** — {item['ingredients'][:60]}...")
                st.markdown(item["recipe"][:300] + "...")
                st.divider()


    weekly_stats = get_weekly_stats()
    if weekly_stats:
        st.divider()
        with st.expander("📊 Статистика питания"):
            st.markdown('<div class="weekly-stats">', unsafe_allow_html=True)
            avg = weekly_stats["average"]
            st.markdown(f"**Приёмов пищи в базе:** {weekly_stats['count']}")

            cols = st.columns(4)
            with cols[0]:
                st.metric("Ср. калории", f"{avg['calories']} ккал")
            with cols[1]:
                st.metric("Ср. белки", f"{avg['proteins']} г")
            with cols[2]:
                st.metric("Ср. жиры", f"{avg['fats']} г")
            with cols[3]:
                st.metric("Ср. углеводы", f"{avg['carbs']} г")
            st.markdown('</div>', unsafe_allow_html=True)



if "profile" not in st.session_state:
    saved = load_profile()
    if saved:
        st.session_state.profile = saved

if "profile" not in st.session_state:
    show_profile_form()
else:
    show_main_screen()
