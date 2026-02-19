import streamlit as st
import time
import pandas as pd
import os

# --- LOGIKA VÝPOČTŮ ---
def vypocitej_bmr(vaha, vyska, vek, pohlavi):
    if vaha == 0 or vyska == 0: return 0
    if pohlavi == 'Muž':
        return (10 * vaha) + (6.25 * vyska) - (5 * vek) + 5
    else:
        return (10 * vaha) + (6.25 * vyska) - (5 * vek) - 161

# --- NASTAVENÍ STRÁNKY ---
st.set_page_config(page_title="PhysioMetrics", page_icon="📊", layout="wide")

st.title("🚀 PHYSIOMETRICS")

# --- SIDEBAR (Osobní údaje) ---
with st.sidebar:
    st.header("👤 Osobní profil")
    jmeno = st.text_input("Jméno uživatele", "")
    pohlavi = st.selectbox("Pohlaví", ["Muž", "Žena"])
    vaha = st.number_input("Váha (kg)", value=0.0, min_value=0.0)
    vyska_cm = st.number_input("Výška (cm)", value=0.0, min_value=0.0)
    vek = st.number_input("Věk", value=0, min_value=0)

# Výpočty základních metrik
bmi = vaha / ((vyska_cm / 100) ** 2) if vyska_cm > 0 else 0
bmr = vypocitej_bmr(vaha, vyska_cm, vek, pohlavi)

# --- HLAVNÍ STRUKTURA (TABY) ---
tab1, tab2, tab3 = st.tabs(["📊 Analýza & Výpočty", "📚 Odborná metodika", "📜 Deník & Historie"])

# --- TAB 1: ANALÝZA & VÝPOČTY ---
with tab1:
    if not jmeno:
        st.info("Zadejte prosím své jméno v levém panelu pro zahájení analýzy.")
    
    st.header(f"Analýza: {jmeno if jmeno else '---'}")
    
    col_bmi, col_bmr = st.columns(2)
    with col_bmi:
        st.metric("Body Mass Index (BMI)", f"{bmi:.1f}")
        if bmi == 0: st.caption("Zadejte údaje vlevo.")
        elif bmi < 18.5: st.markdown("Kategorie: :blue[**Podváha**]")
        elif bmi < 25: st.markdown("Kategorie: :green[**Normální váha**]")
        elif bmi < 30: st.markdown("Kategorie: :orange[**Nadváha**]")
        else: st.markdown("Kategorie: :red[**Obezita**]")

    with col_bmr:
        st.metric("Basal Metabolic Rate (BMR)", f"{bmr:.0f} kcal")
        st.caption("Minimální energetický výdej v klidovém stavu.")

    st.divider()

    st.subheader("🛠️ Monitoring tréninkového zatížení")
    col_tyden, col_mesic = st.columns(2)

    with col_tyden:
        with st.expander("📅 Akutní zátěž (Posledních 7 dní)", expanded=True):
            st.caption("Zadejte délku v minutách a intenzitu na škále RPE 1-10.")
            dny = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
            total_tyden = 0
            cols_dny = st.columns(7)
            for i, den in enumerate(dny):
                with cols_dny[i]:
                    st.markdown(f"**{den}**")
                    m = st.number_input(f"min", min_value=0, value=0, key=f"m_{den}")
                    intenzita = st.slider(f"RPE", 1, 10, 5, key=f"i_{den}")
                    total_tyden += (m * intenzita)
            st.info(f"Celková týdenní zátěž: **{total_tyden} AU**")

    with col_mesic:
        with st.expander("📊 Chronická zátěž (Předchozí 3 týdny)", expanded=True):
            t1 = st.number_input("Týden 1 (AU)", min_value=0, value=0)
            t2 = st.number_input("Týden 2 (AU)", min_value=0, value=0)
            t3 = st.number_input("Týden 3 (AU)", min_value=0, value=0)
            mesicni_prumer = (t1 + t2 + t3 + total_tyden) / 4 if (t1+t2+t3+total_tyden) > 0 else 0
            st.info(f"Dlouhodobý průměr (Chronická): **{mesicni_prumer:.1f} AU**")

    st.divider()

    st.subheader("🎯 Interpretace dat")
    res_acwr, res_trend = st.columns(2)
    ratio = 0
    with res_acwr:
        if mesicni_prumer > 0:
            ratio = total_tyden / mesicni_prumer
            st.metric("ACWR Index", f"{ratio:.2f}")
            if 0.8 <= ratio <= 1.3: st.success("🟢 SWEET SPOT")
            elif ratio > 1.5: st.error("🔴 DANGER ZONE")
            else: st.warning("🔵 DETRAINING")
        else:
            st.write("Pro výpočet ACWR zadejte data.")

    with res_trend:
        if mesicni_prumer > 0:
            posledni_dva = (t3 + total_tyden) / 2
            prvni_dva = (t1 + t2) / 2
            if prvni_dva > 0:
                diff = (posledni_dva - prvni_dva) / prvni_dva
                if abs(diff) < 0.15: st.info("🔄 KONZISTENTNÍ")
                elif diff > 0: st.success("📈 PROGRESIVNÍ")
                else: st.warning("📉 POLEVUJÍCÍ")

    st.divider()

    st.subheader("🍏 Nutriční strategie")
    if total_tyden > 0 and bmr > 0:
        vydej = (total_tyden / 7) * (vaha * 0.0012)
        tdee = (bmr * 1.2) + vydej
        cil = st.radio("Cíl:", ["Redukce", "Udržení", "Svalový růst"], horizontal=True)
        prijem = tdee - 500 if cil == "Redukce" else (tdee if cil == "Udržení" else tdee + 300)
        st.metric("Doporučený denní příjem", f"{prijem:.0f} kcal")
        
        if st.button("💾 Uložit do deníku"):
            try:
                with open("denik.txt", "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%d.%m.%Y')};{jmeno};{ratio:.2f};{prijem:.0f}\n")
                st.success("Data uložena.")
            except: st.error("Chyba zápisu.")
    else:
        st.caption("Doplňte profil a zátěž pro výpočet kalorií.")

# --- TAB 2: ODBORNÁ METODIKA ---
with tab2:
    st.header("Metodický rámec PhysioMetrics")
    
    with st.expander("🔢 Škála RPE a její význam", expanded=True):
        st.write("""
        **RPE (Rate of Perceived Exertion)** je validovaný nástroj pro subjektivní hodnocení intenzity zatížení. 
        Slouží k kvantifikaci vnitřního zatížení organismu, které může být u každého jedince odlišné i při stejném vnějším stimulu.
        """)
        
        st.markdown("""
        | Stupeň | Intenzita | Fyziologické indikátory |
        | :--- | :--- | :--- |
        | **1-3** | **Nízká** | Minimální zvýšení tepové frekvence, volná konverzace. |
        | **4-6** | **Střední** | Zrychlený dech, mluvení v celých větách je možné, ale vyžaduje úsilí. |
        | **7-8** | **Vysoká** | Výrazné pocení, dýchání znemožňuje plynulou mluvu (pouze krátká slova). |
        | **9-10** | **Maximální** | Anaerobní práh, svalové selhání, neschopnost mluvit. |
        """)

    with st.expander("⚖️ ACWR: Analýza tréninkových zón", expanded=True):
        st.write("""
        **ACWR (Acute-Chronic Workload Ratio)** sleduje vztah mezi akutní zátěží (únava) a chronickou zátěží (fitness). 
        Tento poměr je klíčovým prediktorem rizika vzniku nekontaktních zranění.
        """)
        
        st.markdown("""
        ### 🔵 Detraining (< 0.8)
        Stav, kdy je aktuální podnět nižší, než na co je tkáň adaptována. 
        * **Následek:** Dochází k postupné atrofii svalové hmoty, snižování hustoty kostí a desenzitizaci nervosvalových drah. Dlouhodobý detraining zvyšuje riziko zranění při náhlém návratu k původní zátěži.

        ### 🟢 Sweet Spot (0.8 - 1.3)
        Zóna optimální adaptace. 
        * **Následek:** Organismus je schopen efektivně regenerovat, dochází k superkompenzaci a postupnému zvyšování výkonnosti (fitness) bez excesivního rizika přetížení.

        ### 🔴 Danger Zone (> 1.5)
        Kritická zóna maladaptace. 
        * **Následek:** Akutní zátěž výrazně převyšuje chronickou kapacitu tkání. Dochází k mikrotraumatům, která tělo nestíhá opravovat. 
        * **Klinické riziko:** Výrazně se zvyšuje náchylnost k svalovým trhlinám, únavovým zlomeninám a tendinopatiím. Chronické setrvání v této zóně vede k syndromu přetrénování a selhání imunitního systému.
        """)

    with st.expander("🩺 Metabolické metriky (BMI a BMR)", expanded=True):
        st.write("### BMI (Body Mass Index)")
        st.write("""
        Kvantitativní ukazatel poměru tělesné hmotnosti k výšce. Slouží k rychlému screeningu nutričního stavu populace. 
        Ačkoliv nereflektuje složení těla (svaly vs. tuk), je užitečným indikátorem pro stanovení základních rizik spojených s nadváhou či podváhou.
        """)
        
        st.write("### BMR (Basal Metabolic Rate)")
        st.write("""
        Bazální metabolismus představuje množství energie (v kcal) potřebné pro udržení základních vitálních funkcí (krevní oběh, dýchání, termoregulace) v naprostém klidovém stavu. 
        Je základním kamenem pro výpočet celkového energetického výdeje (TDEE).
        """)

# --- TAB 3: HISTORIE ---
with tab3:
    st.header("📜 Historie měření")
    if os.path.exists("denik.txt"):
        with open("denik.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and jmeno:
            user_lines = [l for l in lines if f";{jmeno};" in l]
            for l in user_lines:
                p = l.split(";")
                st.info(f"📅 **{p[0]}** | ACWR: **{p[2]}** | Nutrice: **{p[3].strip()} kcal**")
        elif not jmeno: st.warning("Zadejte jméno pro zobrazení historie.")
        else: st.info("Žádné záznamy.")
    else: st.info("Deník je zatím prázdný.")
