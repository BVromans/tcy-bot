# TCY Bot v5.7

Papertrading bot gebaseerd op **portfolio-basiswaarde** i.p.v. prijs.

## ⚙️ Strategie

- Werkt met een **basiswaarde** (bijv. 5700 USDC)
- **Verkoop** wanneer portfolio-waarde ≥ +3.6% boven basiswaarde
  - Verkoop TCY ter waarde van `basiswaarde × 0.036`
  - Verhoog basiswaarde met +25 USDC
- **Koop** wanneer portfolio-waarde ≤ −3.2% onder basiswaarde
  - Koop TCY ter waarde van `basiswaarde × 0.032`
  - Basiswaarde blijft gelijk
- Alle waarden worden geladen vanuit `.env`
- Volledig **papertrading** (geen echte orders)

## 🧰 Installatie (virtuele omgeving)

Ga naar je bot-map, bijvoorbeeld:
```bash
cd /volume1/tcy-bot
```

Maak een virtuele omgeving aan:
```bash
python3 -m venv venv
```

Activeer deze:

**Linux / macOS:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\activate
```

Installeer de vereiste pakketten:
```bash
pip install aiohttp python-dotenv
```

Controleer eventueel:
```bash
pip list
```

## 📄 Voorbeeld .env

```env
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
WALLET_ADDRESS=thor1n7y5j4swnq3ufqf6ywzk65mu7stdtwv45dc3gy
PAIR=TCY_USDC
POLL_INTERVAL=60
TRADE_COOLDOWN=60

BASE_VALUE=5700
SELL_DELTA=0.036
BUY_DELTA=-0.032
BASE_INCREMENT=25

# Startportfolio
INITIAL_TCY=33187
INITIAL_PORTFOLIO_VALUE=5700
```

## 🧮 Berekeningen

```
portfolio = (TCY_balance × TCY_price) + USDC_balance
```

- SELL bij `portfolio ≥ base × (1 + SELL_DELTA)`
- BUY bij  `portfolio ≤ base × (1 + BUY_DELTA)`

Na elke verkoop:
```
base += BASE_INCREMENT
```

## ⏱️ Cooldown
Na iedere trade wacht de bot het aantal seconden dat je in `.env` hebt ingesteld als `TRADE_COOLDOWN`, zodat dubbele trades bij kleine koersschommelingen worden voorkomen.

## 📊 Logging & uitvoeren

### Start de bot
```bash
python tcy_bot_v5.7.py
```

### Bekijk log live
```bash
tail -f /volume1/tcy-bot/tcy_bot.log
```

### Stop logweergave
Druk `Ctrl + C`

Logbestanden:
- `tcy_bot.log` → logboek
- `trades.csv` → alle uitgevoerde transacties

## 📲 Telegram voorbeelden

```
🚀 TCY Bot v5.7 gestart | Base=$5700.00 | Portfolio=33,187 TCY | Δ+3.6% / -3.2%
💰 SELL uitgevoerd | Δ+3.6% | Verkocht $205.20 | Nieuwe base=$5725.00 | TCY=33000.00
🛒 BUY uitgevoerd | Δ-3.2% | Gekocht $182.40 | Base=$5700.00 | TCY=33187.00
🕐 Cooldown actief (60s)...
```

---

## 🧹 Geavanceerd GitHub-onderhoud

### 🔒 Gevoelige bestanden volledig uit Git-geschiedenis verwijderen

Gebruik `git filter-repo` om gevoelige of oude bestanden (zoals `.env`) uit de gehele commitgeschiedenis te wissen.

1️⃣ Installeer `git filter-repo`:
```bash
pip install git-filter-repo
```

2️⃣ Maak een mirror-clone:
```bash
cd ~
git clone --mirror https://github.com/BVromans/tcy-bot.git tcy-bot-clean
```

3️⃣ Ga naar de map:
```bash
cd ~/tcy-bot-clean
```

4️⃣ Verwijder de ongewenste bestanden uit alle commits:
```bash
git filter-repo \
  --path .env \
  --path readme.txt \
  --path tcy_bot_v_4_0.py \
  --invert-paths
```

5️⃣ Herkoppel de remote en push de opgeschoonde repo:
```bash
git remote add origin https://github.com/BVromans/tcy-bot.git
git push --mirror origin
```

6️⃣ Controleer online of `.env`, `readme.txt`, en `tcy_bot_v_4_0.py` volledig verdwenen zijn.

7️⃣ Verwijder de tijdelijke map:
```bash
cd ~
rm -rf tcy-bot-clean
```

### 🏡 Herstellen van lokale omgeving

1️⃣ Ga terug naar je originele project:
```bash
cd /volume1/tcy-bot
```

2️⃣ Controleer status:
```bash
git status
```

3️⃣ Herstel `.env` en verwijder oude bestanden:
```bash
git restore .env
git add .gitignore
git rm readme.txt tcy_bot_v_4_0.py
git commit -m "Clean up local repo: remove legacy files and update gitignore"
```

4️⃣ Push veranderingen:
```bash
git push
```

Als je de melding krijgt:
```
! [rejected] main -> main (fetch first)
```
Voer dan eerst uit:
```bash
git pull --rebase origin main
```
Daarna:
```bash
git push
```

Gebruik als alternatief (indien je jouw lokale versie wilt forceren):
```bash
git push --force
```

5️⃣ Controleer tenslotte:
```bash
git status
```
Moet weergeven:
```
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

