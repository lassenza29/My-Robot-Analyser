import streamlit as st
import yfinance as yf
import math

# Configuration de la page (Mode Pro)
st.set_page_config(page_title="Analyseur Financier Pro", page_icon="🏛️", layout="wide")

st.title("🏛️ Analyseur Financier Professionnel (Actions & ETF)")
st.markdown("Outil de filtrage algorithmique basé sur les critères stricts de valorisation et de sécurité financière.")

# Saisie du Ticker
ticker_symbole = st.text_input("🔍 Entrez le symbole (ex: AAPL, TTE.PA, CW8.PA, SPY) :", value="AAPL").upper().strip()

if ticker_symbole:
    with st.spinner(f"Extraction des données financières pour {ticker_symbole}..."):
        try:
            action = yf.Ticker(ticker_symbole)
            info = action.info

            if not info or ('shortName' not in info and 'longName' not in info):
                st.error("❌ Symbole introuvable. Vérifiez l'orthographe (ex: ajoutez .PA pour la bourse de Paris).")
            else:
                # --- FONCTIONS DE SÉCURITÉ (Zéro plantage) ---
                def get_float(key, mult=1.0, default=0.0):
                    val = info.get(key)
                    if val is None: return default
                    try: return float(val) * mult
                    except (ValueError, TypeError): return default

                def get_str(key, default="N/A"):
                    val = info.get(key)
                    return str(val).strip() if val is not None else default

                quote_type = get_str('quoteType').upper()
                nom_entreprise = info.get('longName') or info.get('shortName') or ticker_symbole

                # =========================================================
                # MODE ETF : ANALYSE SELON LES 5 CRITÈRES
                # =========================================================
                if quote_type == "ETF":
                    st.header(f"📊 Analyse de l'ETF : {nom_entreprise}")
                    
                    frais = get_float('expenseRatio', 100.0)
                    encours = get_float('totalAssets', 1 / 1_000_000)
                    rendement = get_float('trailingAnnualDividendYield', 100.0) or get_float('yield', 100.0)
                    
                    st.markdown("### Les Critères Fondamentaux de l'ETF")
                    
                    # Critère 1 : Frais
                    st.markdown("#### 1. Frais de gestion (TER)")
                    if 0 < frais <= 0.30:
                        st.success(f"🟢 **{frais:.2f} %** : Excellent. Les frais sont très bas, idéal pour le long terme.")
                    elif frais > 0.30:
                        st.warning(f"⚠️ **{frais:.2f} %** : Modéré à élevé. (Cible idéale < 0.30%).")
                    else:
                        st.info("⚪ Non communiqué par l'API pour ce fonds.")

                    # Critère 2 & 3 : Encours et Liquidité
                    st.markdown("#### 2 & 3. Volume de l'encours et Liquidité")
                    if encours >= 100:
                        st.success(f"🟢 **{encours:,.1f} M$** : Excellent. Le fonds est massif, très liquide et le risque de clôture est nul.")
                    elif 50 <= encours < 100:
                        st.warning(f"⚠️ **{encours:,.1f} M$** : Acceptable mais à surveiller (proche du seuil de 50 M$).")
                    else:
                        st.error(f"🔴 **{encours:,.1f} M$** : Danger. Le fonds est trop petit, risque élevé de liquidation.")

                    # Critère 4 & 5 : Réplication et Distribution
                    st.markdown("#### 4 & 5. Mode de Distribution & Réplication")
                    if rendement > 0:
                        st.info(f"💶 **ETF Distribuant :** Rendement de {rendement:.2f}%. \n\n*Rappel stratégique : Si vous investissez sur un CTO, la distribution de dividendes déclenchera l'imposition de la Flat Tax chaque année. Privilégiez cet ETF dans une enveloppe sans frottement fiscal immédiat, ou cherchez son équivalent Capitalisant (Acc).*")
                    else:
                        st.success("🔄 **ETF Capitalisant (ou distribution non détectée) :** Idéal pour profiter des intérêts composés et optimiser la fiscalité sur un CTO.")
                    st.caption("ℹ️ *Note : Le mode de réplication (Physique/Synthétique) et le Tracking Error exact doivent être vérifiés sur le DICI (Document d'Information Clé) de l'émetteur.*")

                # =========================================================
                # MODE ACTION : LES 21 RATIOS ET CRITÈRES
                # =========================================================
                else:
                    st.header(f"🏢 Analyse Fondamentale : {nom_entreprise}")
                    st.markdown("Tableau de bord structuré selon les **21 points d'analyse exigés**.")

                    # --- EXTRACTION DES 21 POINTS ---
                    p_nom = nom_entreprise # 2
                    p_prix = get_float('currentPrice') or get_float('regularMarketPrice') # 3
                    p_cap = get_float('marketCap', 1 / 1_000_000) # 4
                    p_dette_b = get_float('totalDebt', 1 / 1_000_000) # 5
                    p_treso = get_float('totalCash', 1 / 1_000_000) # 6
                    p_dette_n = p_dette_b - p_treso # 7
                    p_ebitda = get_float('ebitda', 1 / 1_000_000) # 8
                    p_ratio_d_e = p_dette_n / p_ebitda if p_ebitda > 0 else 0.0 # 9
                    
                    p_ca = get_float('totalRevenue', 1 / 1_000_000) # 10
                    p_res_expl = get_float('operatingIncome', 1 / 1_000_000) or get_float('operatingCashflow', 1 / 1_000_000) # 11
                    p_res_net = get_float('netIncomeToCommon', 1 / 1_000_000) # 12
                    p_marge_expl = get_float('operatingMargins', 100.0) # 13
                    p_marge_net = get_float('profitMargins', 100.0) # 14
                    
                    # Extraction anticipée pour éviter les erreurs d'ordre d'exécution
                    p_actions = get_float('sharesOutstanding') # 17
                    p_actif_net_a = get_float('bookValue') # 20

                    # 15. Capitaux Propres (avec calcul de secours si Yahoo Finance renvoie 0)
                    p_cp = get_float('totalStockholderEquity', 1 / 1_000_000) 
                    if p_cp == 0 and p_actif_net_a > 0 and p_actions > 0:
                        p_cp = (p_actif_net_a * p_actions) / 1_000_000

                    p_roe = get_float('returnOnEquity', 100.0) # 16
                    p_bna = get_float('trailingEps') or get_float('forwardEps') # 18
                    p_per = get_float('trailingPE') # 19
                    
                    # 21 : Prix de Graham (Sécurisé)
                    produit_graham = 22.5 * p_bna * p_actif_net_a
                    p_graham = math.sqrt(produit_graham) if produit_graham > 0 else 0.0

                    # 1 : Ratio & Critère (Verdict global)
                    is_safe = (p_dette_n <= 0) or (p_ratio_d_e < 3)
                    is_profitable = (p_marge_expl > 8) and (p_roe > 10)
                    is_cheap = (0 < p_prix < p_graham)

                    # --- AFFICHAGE DE L'INTERFACE DES ACTIONS ---
                    st.divider()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("2. Nom de l'entreprise", p_nom)
                    col2.metric("3. Prix actuel", f"{p_prix:,.2f} $")
                    col3.metric("4. Capitalisation (M)", f"{p_cap:,.0f} M$")
                    col4.metric("17. Actions en circulation", f"{p_actions:,.0f}" if p_actions else "N/A")

                    st.markdown("### Structure Financière (Dette & Trésorerie)")
                    col5, col6, col7, col8 = st.columns(4)
                    col5.metric("5. Dette Brute (M)", f"{p_dette_b:,.0f} M$")
                    col6.metric("6. Trésorerie (M)", f"{p_treso:,.0f} M$")
                    col7.metric("7. Dette Nette (M)", f"{p_dette_n:,.0f} M$")
                    col8.metric("15. Capitaux Propres (M)", f"{p_cp:,.0f} M$")

                    col9, col10, col11, col12 = st.columns(4)
                    col9.metric("8. EBITDA (M)", f"{p_ebitda:,.0f} M$")
                    with col10:
                        st.metric("9. Ratio Dette Nette / EBITDA", f"{p_ratio_d_e:.2f} x")
                        if p_dette_n <= 0: st.caption("🟢 Cash Net")
                        elif p_ratio_d_e < 3: st.caption("🟢 Maîtrisé (< 3)")
                        else: st.caption("🔴 Trop endetté (> 3)")

                    st.markdown("### Performance & Marges")
                    col13, col14, col15, col16 = st.columns(4)
                    col13.metric("10. Chiffre d'affaires (M)", f"{p_ca:,.0f} M$")
                    col14.metric("11. Résultat d'exploitation (M)", f"{p_res_expl:,.0f} M$")
                    col15.metric("12. Résultat Net (M)", f"{p_res_net:,.0f} M$")
                    with col16:
                        st.metric("16. ROE", f"{p_roe:.2f} %")
                        st.caption("🟢 Bon" if p_roe > 10 else "🔴 Faible")

                    col17, col18, col19, col20 = st.columns(4)
                    with col17:
                        st.metric("13. Marge d'exploitation", f"{p_marge_expl:.2f} %")
                        st.caption("🟢 Bonne" if p_marge_expl > 8 else "🔴 Faible")
                    col18.metric("14. Marge Nette", f"{p_marge_net:.2f} %")

                    st.markdown("### Valorisation & Multiples")
                    col21, col22, col23, col24 = st.columns(4)
                    col21.metric("18. BNA", f"{p_bna:.2f} $")
                    with col22:
                        st.metric("19. PER", f"{p_per:.2f} x" if p_per > 0 else "N/A")
                        if p_per > 0: st.caption("🟢 Bon" if p_per < 20 else "🔴 Cher")
                    col23.metric("20. Actif Net par Action", f"{p_actif_net_a:.2f} $")
                    with col24:
                        st.metric("21. Prix Juste Graham", f"{p_graham:.2f} $" if p_graham > 0 else "N/A")
                        if p_graham > 0: st.caption("🟢 Sous-évalué" if p_prix < p_graham else "🔴 Surévalué")

                    # 1. Ratio & Critère (Verdict Final)
                    st.divider()
                    st.markdown("### 1. Ratio & Critère (Verdict Final)")
                    if is_safe and is_profitable:
                        if is_cheap:
                            st.success("✅ **ENTREPRISE VALIDÉE ET SOUS-ÉVALUÉE :** La santé financière est solide, les marges sont excellentes, et le prix de l'action est inférieur à la valeur théorique de Graham. C'est une excellente opportunité.")
                            st.balloons()
                        else:
                            st.warning("⚠️ **BELLE ENTREPRISE, MAIS CHÈRE :** L'entreprise est très qualitative (dette maîtrisée, fortes marges), mais le prix du marché est actuellement supérieur à sa valeur intrinsèque de Graham. À surveiller pour un repli.")
                    else:
                        st.error("❌ **ENTREPRISE RECALÉE :** L'action ne passe pas vos critères stricts de sécurité. Soit la dette est trop élevée, soit les marges et la rentabilité sont insuffisantes.")

        except Exception as e:
            st.error(f"Erreur système critique : {e}")
