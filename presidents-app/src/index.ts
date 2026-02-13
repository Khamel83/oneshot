import { Client } from "pg";

// Fun facts for some presidents
const funFacts: Record<string, string> = {
  "Washington": "Wore dentures made of hippopotamus ivory",
  "Lincoln": "Was a skilled wrestler with nearly 300 matches",
  "Teddy Roosevelt": "Was shot mid-speech but kept talking for 90 minutes",
  "Kennedy": "Won a Pulitzer Prize for his book",
  "Nixon": "Was an excellent poker player in the Navy",
  "Reagan": "Started his career as a radio sports announcer",
  "Obama": "Has won two Grammy Awards for audiobooks",
  "Trump": "Had a cameo in Home Alone 2",
  "Biden": "Overcame a childhood stutter",
  "Cleveland": "Only president to serve non-consecutive terms",
  "FDR": "Related to 11 other presidents",
  "Taft": "Got stuck in the White House bathtub",
  "Van Buren": "First president born as a US citizen",
  "Jefferson": "Invented the swivel chair",
  "Adams": "Liked to skinny dip in the Potomac",
};

export default {
  async fetch(request, env, ctx) {
    const client = new Client({ connectionString: env.HYPERDRIVE.connectionString });
    await client.connect();

    const result = await client.query(
      "SELECT * FROM presidents ORDER BY last_name DESC"
    );
    await client.end();

    const html = `<!DOCTYPE html>
<html>
<head>
  <title>🇺🇸 US Presidents</title>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+Pro:wght@400;600&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: 'Source Sans Pro', sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      min-height: 100vh;
      margin: 0;
      padding: 20px;
      color: white;
    }
    .container {
      max-width: 900px;
      margin: 0 auto;
    }
    header {
      text-align: center;
      padding: 40px 20px;
      position: relative;
    }
    h1 {
      font-family: 'Playfair Display', serif;
      font-size: 3rem;
      margin: 0;
      background: linear-gradient(90deg, #e94560, #f39c12, #fff);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      animation: shimmer 3s ease-in-out infinite;
    }
    @keyframes shimmer {
      0%, 100% { filter: brightness(1); }
      50% { filter: brightness(1.2); }
    }
    .stars {
      font-size: 2rem;
      margin: 10px 0;
      animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.1); }
    }
    .count {
      font-size: 1.2rem;
      color: #a0a0a0;
      margin-top: 10px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
      padding: 20px 0;
    }
    .president-card {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 16px;
      padding: 20px;
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;
    }
    .president-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(90deg, #e94560, #f39c12);
    }
    .president-card:hover {
      transform: translateY(-5px);
      background: rgba(255,255,255,0.1);
      box-shadow: 0 10px 40px rgba(233, 69, 96, 0.2);
    }
    .president-name {
      font-family: 'Playfair Display', serif;
      font-size: 1.4rem;
      margin: 0 0 8px 0;
    }
    .president-term {
      color: #f39c12;
      font-weight: 600;
      font-size: 0.9rem;
    }
    .president-fact {
      margin-top: 12px;
      font-size: 0.85rem;
      color: #a0a0a0;
      font-style: italic;
      line-height: 1.4;
    }
    .president-number {
      position: absolute;
      top: 15px;
      right: 15px;
      font-size: 2rem;
      font-weight: bold;
      opacity: 0.1;
      font-family: 'Playfair Display', serif;
    }
    footer {
      text-align: center;
      padding: 40px;
      color: #666;
      font-size: 0.9rem;
    }
    footer a { color: #e94560; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="stars">⭐ 🦅 ⭐</div>
      <h1>US Presidents</h1>
      <p class="count">${result.rows.length} commanders in chief, sorted by last name (Z→A)</p>
    </header>
    
    <div class="grid">
      ${result.rows.map((p, i) => `
        <div class="president-card">
          <span class="president-number">#${i + 1}</span>
          <h2 class="president-name">${p.first_name} ${p.last_name}</h2>
          <div class="president-term">🏛️ ${p.term_start}–${p.term_end}</div>
          ${funFacts[p.last_name] ? `<div class="president-fact">💡 ${funFacts[p.last_name]}</div>` : ''}
        </div>
      `).join('')}
    </div>
    
    <footer>
      Built with ONE_SHOT • Data from your Postgres • Powered by Cloudflare Workers + Hyperdrive
    </footer>
  </div>
</body>
</html>`;

    return new Response(html, {
      headers: { "content-type": "text/html;charset=UTF-8" }
    });
  },
};
