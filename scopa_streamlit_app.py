import streamlit as st
import random
import collections
import itertools

# --- Definizione carte ---
suits = ['B', 'C', 'D', 'S']
values = list(range(1, 11))
deck = [f"{v}{s}" for v in values for s in suits]
point_map = {7: 21, 6: 18, 1: 16, 5: 15, 4: 14, 3: 13, 2: 12, 10: 10, 9: 10, 8: 10}

st.title("♠️ Scopa Strategica – Simulazione Monte Carlo")

# --- Selezione carte viste ---
st.sidebar.header("Carte viste (giocate, raccolte, in tavola)")
seen_cards = []
for v in values:
    cols = st.sidebar.columns(4)
    for i, s in enumerate(suits):
        label = f"{v}{s}"
        if cols[i].checkbox(label):
            seen_cards.append(label)

unknown_cards = [c for c in deck if c not in seen_cards]

# --- Simula mano avversaria ---
st.header("🔮 Simula Probabilità carte avversario")
if len(unknown_cards) < 3:
    st.error("Non ci sono abbastanza carte residue per simulare la mano avversaria.")
else:
    simulations = 10000
    count_cards = collections.Counter()
    settebello_count = 0

    for _ in range(simulations):
        sampled = random.sample(unknown_cards, 3)
        for card in sampled:
            count_cards[card] += 1
        if "7D" in sampled:
            settebello_count += 1

    with st.expander("Mostra probabilità per ogni carta"): 
        for card in sorted(count_cards, key=lambda x: (int(x[:-1]), x[-1])):
            prob = count_cards[card] / simulations
            st.write(f"{card}: {prob:.2%}")

    st.info(f"🎯 Probabilità che l'avversario abbia il 7 di denari (7D): {settebello_count / simulations:.2%}")

# --- Analizza rischio scopa ---
st.header("⚠️ Analisi Rischio Scopa")
play_card = st.text_input("Carta che vuoi giocare (es. 6C)")
table_input = st.text_input("Carte sul tavolo separate da virgola (es. 1C,2D,3B)")

table_cards = [c.strip().upper() for c in table_input.split(',') if c.strip()]
if play_card and table_cards:
    try:
        val = int(play_card[:-1])
        valid_sums = set()
        for i in range(1, len(table_cards)+1):
            for combo in itertools.combinations(table_cards, i):
                total = sum(int(c[:-1]) for c in combo)
                valid_sums.add(total)

        if val not in valid_sums:
            st.success("✅ Nessuna combinazione sul tavolo produce una scopa con la carta giocata.")
        else:
            risk_count = 0
            for _ in range(simulations):
                sampled = random.sample(unknown_cards, 3)
                if any(int(c[:-1]) == val for c in sampled):
                    risk_count += 1
            st.warning(f"Rischio che l'avversario possa fare scopa con {play_card.upper()}: {risk_count / simulations:.2%}")
    except:
        st.error("Inserisci una carta valida (es. 6C) e carte tavolo corrette.")

# --- Analisi Primiera ---
st.header("🏆 Analisi Primiera")
if len(unknown_cards) >= 3:
    total_points = []
    for _ in range(simulations):
        hand = random.sample(unknown_cards, 3)
        best = {'B': 0, 'C': 0, 'D': 0, 'S': 0}
        for c in hand:
            val, s = int(c[:-1]), c[-1]
            if point_map.get(val, 0) > point_map.get(best[s], 0):
                best[s] = val
        score = sum(point_map.get(v, 0) for v in best.values())
        total_points.append(score)
    avg = sum(total_points) / simulations
    st.info(f"Media punti primiera avversario: {avg:.2f}")

# --- Suggerimento automatico ---
st.header("🤖 Suggerimento automatico su cosa giocare")
hand_input = st.text_input("Tua mano (es. 1C,6D,10S)")
table_input2 = st.text_input("Carte sul tavolo (es. 2C,4S,5B)")

hand = [c.strip().upper() for c in hand_input.split(',') if c.strip()]
table2 = [c.strip().upper() for c in table_input2.split(',') if c.strip()]

if hand and table2:
    risks = {}
    for card in hand:
        try:
            val = int(card[:-1])
        except:
            continue
        valid_sums = set()
        for i in range(1, len(table2)+1):
            for combo in itertools.combinations(table2, i):
                try:
                    total = sum(int(c[:-1]) for c in combo)
                    valid_sums.add(total)
                except:
                    continue
        if val in valid_sums:
            risk = 0
            for _ in range(1000):
                sample = random.sample(unknown_cards, 3)
                if any(int(c[:-1]) == val for c in sample):
                    risk += 1
            risks[card] = risk / 1000
        else:
            risks[card] = 0.0

    safest = min(risks.items(), key=lambda x: x[1])
    for c, r in risks.items():
        st.write(f"{c}: rischio scopa avversario {r:.2%}")
    st.success(f"👉 Gioca {safest[0]} (rischio minimo)")
