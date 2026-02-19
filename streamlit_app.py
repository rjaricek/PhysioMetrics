import streamlit as st
import time
import pandas as pd
import os

# --- LOGIKA VÝPOČTŮ ---
def vypocitej_bmr(vaha, vyska, vek, pohlavi):
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
    jmeno = st.text_input("Jak ti mám říkat?", "Ráďo")
    pohlavi = st.selectbox("Pohlaví", ["Muž", "Žena"])
    vaha = st.number_input("Váha (kg)", value=80.0, min_value=10.0)
    vyska_cm = st.number_input("Výška (cm)", value=180.0, min_value=50.0)
    vek = st.number_input("Věk", value=30, min_value=1)

# Výpočty základních metrik
vyska_m = vyska_cm / 100
bmi = vaha / (vyska_m ** 2)
bmr = vypocitej_bmr(vaha, vyska_cm, vek, pohlavi)

# --- HLAVNÍ STRUKTURA (TABY) ---
tab1, tab2, tab3 = st.tabs(["📊 Analýza & Výpočty", "📚 Teorie & Vysvětlivky", "📜 Deník & Historie"])

# --- TAB 1: ANALÝZA & VÝPOČTY ---
with tab1:
    st.header(f"Analýza pro uživatele: {jmeno}")
    
    col_bmi, col_bmr = st.columns(2)
    with col_bmi:
        st.metric("Tvoje BMI", f"{bmi:.1f}")
        if bmi < 18.5: kat, barva = "Podváha", "blue"
        elif bmi < 25: kat, barva = "Normální váha", "green"
        elif bmi < 30: kat, barva = "Nadváha", "orange"
        else: kat, barva = "Obezita", "red"
        st.markdown(f"Kategorie: :{barva}[**{kat}**]")

    with col_bmr:
        st.metric("BMR (Bazální metabolismus)", f"{bmr:.0f} kcal")
        st.write("🔥 Minimální energie pro přežití.")

    st.divider()

    # Sekce ACWR Kalkulačky
    st.subheader("🛠️ Kalkulačky tréninkové zátěže")
    col_tyden, col_mesic = st.columns(2)

    with col_tyden:
        with st.expander("📅 Týdenní zátěž (Akutní)", expanded=True):
            st.caption("💡 **RPE:** 1-2 (lehké), 5-6 (střední), 7-8 (těžké), 9-10 (max)")
            dny = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]
            total_tyden = 0
            cols_dny = st.columns(7)
            for i, den in enumerate(dny):
                with cols_dny[i]:
                    st.markdown(f"**{den}**")
                    m = st.number_input(f"min", min_value=0, value=0, key=f"m_{den}")
                    intenzita = st.slider(f"RPE", 1, 10, 5, key=f"i_{den}")
                    total_tyden += (m * intenzita)
            st.info(f"Součet týdenní zátěže: **{total_tyden}**")

    with col_mesic:
        with st.expander("📊 Měsíční zátěž (Chronická)", expanded=True):
            t1 = st.number_input("Týden 1 (zátěž)", min_value=0, value=0)
            t2 = st.number_input("Týden 2 (zátěž)", min_value=0, value=0)
            t3 = st.number_input("Týden 3 (zátěž)", min_value=0, value=0)
            st.write(f"Týden 4 (Aktuální): **{total_tyden}**")
            
            mesicni_sum = t1 + t2 + t3 + total_tyden
            mesicni_prumer = mesicni_sum / 4 if mesicni_sum > 0 else 0
            st.info(f"Dlouhodobý průměr: **{mesicni_prumer:.1f}**")

    st.divider()

    # Verdikt a Trend
    st.subheader("🎯 Výsledný verdikt")
    res_acwr, res_trend = st.columns(2)
    ratio = 0
    with res_acwr:
        if mesicni_prumer > 0 and total_tyden > 0:
            ratio = total_tyden / mesicni_prumer
            st.metric("ACWR Index", f"{ratio:.2f}")
            if 0.8 <= ratio <= 1.3: st.success("🟢 SWEET SPOT")
            elif ratio > 1.5: st.error("🔴 DANGER ZONE")
            else: st.warning("🔵 DETRAINING")
        else:
            st.info("Zadejte data pro výpočet ACWR.")

    with res_trend:
        st.metric("Konzistence (Dlouhodobý průměr)", f"{mesicni_prumer:.0f}")
        if mesicni_prumer > 0:
            posledni_dva = (t3 + total_tyden) / 2
            prvni_dva = (t1 + t2) / 2
            if prvni_dva > 0:
                diff = (posledni_dva - prvni_dva) / prvni_dva
                if abs(diff) < 0.15: st.info("🔄 KONZISTENTNÍ")
                elif diff > 0: st.success("📈 PROGRESIVNÍ")
                else: st.warning("📉 POLEVUJÍCÍ")
            else:
                st.write("Zadej i starší týdny pro analýzu trendu.")

    st.divider()

    # Nutrice
    st.subheader("🍏 Nutriční strategie")
    if total_tyden > 0:
        denni_treninkovy_vydej = (total_tyden / 7) * (vaha * 0.0012)
        tdee = (bmr * 1.2) + denni_treninkovy_vydej
        cil = st.radio("Cíl:", ["Chci zhubnout", "Udržet kondici", "Nabrat svaly"], horizontal=True)
        
        prijem = tdee - 500 if cil == "Chci zhubnout" else (tdee if cil == "Udržet kondici" else tdee + 300)
        st.metric("Doporučený denní příjem", f"{prijem:.0f} kcal")
        
        if st.button("💾 Uložit dnešní výsledky"):
            datum = time.strftime("%d.%m.%Y")
            radek = f"{datum};{jmeno};{ratio:.2f};{mesicni_prumer:.1f};{prijem:.0f}\n"
            try:
                with open("denik.txt", "a", encoding="utf-8") as f:
                    f.write(radek)
                st.success("Záznam byl úspěšně přidán do PhysioMetrics!")
                st.balloons()
            except Exception as e:
                st.error(f"Chyba při ukládání: {e}")
    else:
        st.warning("Zadejte alespoň jeden tréninkový den pro výpočet.")

# --- TAB 2: VYSVĚTLIVKY ---
with tab2:
    st.header("📚 Odborný průvodce metodikou PhysioMetrics")
    
    with st.expander("🔢 Škála RPE (Subjektivní intenzita)"):
        st.write("RPE (Rate of Perceived Exertion) měří intenzitu tréninku.")
        
        st.markdown("""
        | RPE | Náročnost | Popis |
        | :--- | :--- | :--- |
        | 1-3 | Lehká | Chůze, protažení, můžete si zpívat |
        | 4-6 | Střední | Rychlejší pohyb, mluvíte v celých větách |
        | 7-8 | Těžká | Velmi intenzivní, mluvíte jen v krátkých slovech |
        | 9-10 | Maximální | Sprint, na pokraji sil, nelze mluvit |
        """)

    with st.expander("⚖️ ACWR a Prevence zranění"):
        st.write("Poměr mezi akutní (7 dní) a chronickou (28 dní) zátěží.")
        
        st.markdown("""
        * **🟢 0.8 - 1.3 (Sweet Spot):** Bezpečný prostor pro zvyšování kondice.
        * **🔴 > 1.5 (Danger Zone):** Vysoké riziko zranění (přetížení).
        """)

# --- TAB 3: HISTORIE ---
with tab3:
    st.header("📜 Historie měření")
    
    if os.path.exists("denik.txt"):
        with open("denik.txt", "r", encoding="utf-8") as f:
            vsechna_data = f.readlines()
        
        moje_data = [line for line in vsechna_data if f";{jmeno};" in line]
        
        if moje_data:
            st.write(f"Záznamy pro uživatele: **{jmeno}**")
            for d in moje_data:
                p = d.split(";")
                st.info(f"📅 **{p[0]}** | ACWR: **{p[2]}** | Cílové kalorie: **{p[4].strip()} kcal**")
        else:
            st.info(f"Ahoj {jmeno}! Vypadá to, že tvůj deník je zatím prázdný. Ulož si své první měření v záložce Analýza.")
    else:
        st.info("Zatím nebyla uložena žádná data. Buď první!")
