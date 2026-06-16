INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS Demo Coach AI</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #070a10;
      --bg-soft: #0b1018;
      --panel: #101722;
      --panel-2: #151f2e;
      --panel-3: #0b111a;
      --line: #263447;
      --line-strong: #3a4f69;
      --text: #edf3ff;
      --muted: #9aa9bc;
      --muted-2: #718196;
      --red: #ff4d4d;
      --orange: #ff9f1c;
      --green: #33d17a;
      --blue: #5aa9ff;
      --purple: #b388ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    body::before {
      content: "";
      position: fixed;
      inset: 0;
      z-index: -2;
      background:
        linear-gradient(180deg, rgba(7, 10, 16, 0.12), var(--bg) 70%),
        url("/static/maps/de_mirage_radar.png") center top / min(900px, 95vw) no-repeat,
        var(--bg);
      opacity: 0.32;
      filter: saturate(1.15);
    }
    body::after {
      content: "";
      position: fixed;
      inset: 0;
      z-index: -1;
      background:
        linear-gradient(135deg, rgba(255, 159, 28, 0.12), transparent 36%),
        linear-gradient(215deg, rgba(90, 169, 255, 0.10), transparent 34%),
        rgba(7, 10, 16, 0.76);
      pointer-events: none;
    }
    main {
      max-width: 1320px;
      margin: 0 auto;
      padding: 30px 22px 56px;
    }
    h1, h2, h3, p { margin-top: 0; }
    h1 {
      margin-bottom: 14px;
      font-size: clamp(42px, 6vw, 76px);
      line-height: 0.95;
      letter-spacing: 0;
    }
    h2 {
      margin: 0;
      font-size: 22px;
      letter-spacing: 0;
    }
    h3 {
      margin: 0;
      font-size: 17px;
      letter-spacing: 0;
    }
    button,
    input,
    select {
      font: inherit;
    }
    input,
    select {
      min-height: 46px;
      width: 100%;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0a1019;
      color: var(--text);
      outline: none;
      transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }
    input:focus,
    select:focus {
      border-color: var(--orange);
      box-shadow: 0 0 0 3px rgba(255, 159, 28, 0.14);
      background: #0d1420;
    }
    input[type="range"] {
      width: 100%;
      min-height: 28px;
      padding: 0;
      accent-color: var(--orange);
      box-shadow: none;
    }
    button {
      min-height: 44px;
      padding: 10px 16px;
      border: 0;
      border-radius: 8px;
      background: var(--orange);
      color: #140f08;
      font-weight: 850;
      cursor: pointer;
      white-space: nowrap;
      transition: transform 160ms ease, filter 160ms ease, background 160ms ease, border-color 160ms ease;
    }
    button:hover:not(:disabled) {
      transform: translateY(-1px);
      filter: brightness(1.08);
    }
    button:disabled {
      opacity: 0.6;
      cursor: wait;
    }
    .secondary-button {
      border: 1px solid var(--line);
      background: #0c1320;
      color: var(--text);
    }
    .ghost-button {
      border: 1px solid var(--line);
      background: transparent;
      color: var(--text);
    }
    .product-topbar {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: center;
      margin-bottom: 24px;
    }
    .brand-lockup {
      display: flex;
      align-items: center;
      gap: 12px;
      color: var(--text);
      font-weight: 900;
    }
    .brand-mark {
      display: grid;
      place-items: center;
      width: 38px;
      height: 38px;
      border: 1px solid rgba(255, 159, 28, 0.45);
      border-radius: 8px;
      background: rgba(255, 159, 28, 0.12);
      color: var(--orange);
      font-weight: 950;
    }
    .status-pill,
    .badge {
      display: inline-flex;
      align-items: center;
      width: fit-content;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 850;
      white-space: nowrap;
    }
    .status-pill {
      border: 1px solid var(--line);
      padding: 8px 12px;
      background: rgba(12, 19, 32, 0.78);
      color: var(--muted);
    }
    .landing {
      display: grid;
      gap: 22px;
    }
    .hero {
      position: relative;
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) 420px;
      gap: 28px;
      align-items: end;
      min-height: 590px;
      padding: 34px;
      border: 1px solid rgba(58, 79, 105, 0.78);
      border-radius: 8px;
      overflow: hidden;
      background:
        linear-gradient(90deg, rgba(7, 10, 16, 0.98), rgba(7, 10, 16, 0.74) 48%, rgba(7, 10, 16, 0.92)),
        url("/static/maps/de_mirage_radar.png") right center / min(680px, 58vw) no-repeat,
        #090e16;
      box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
    }
    .hero-copy {
      max-width: 760px;
      align-self: center;
    }
    .eyebrow {
      margin-bottom: 12px;
      color: var(--orange);
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .subtitle {
      max-width: 680px;
      margin-bottom: 0;
      color: #d8e3f2;
      font-size: 19px;
      line-height: 1.55;
    }
    .hero-proof {
      display: flex;
      gap: 9px;
      flex-wrap: wrap;
      margin-top: 24px;
    }
    .hero-proof span {
      display: inline-flex;
      padding: 8px 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(11, 17, 26, 0.78);
      color: #d9e3f1;
      font-size: 13px;
      font-weight: 800;
    }
    .upload-panel,
    .feature-card,
    .loading-panel,
    .section,
    .metric-card,
    .round-review-card,
    .round-card,
    .focus-card,
    .debug-card,
    .error-card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(16, 23, 34, 0.94);
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22);
    }
    .upload-panel {
      padding: 20px;
      backdrop-filter: blur(14px);
    }
    .upload-panel h2 {
      margin-bottom: 6px;
    }
    .panel-copy {
      margin-bottom: 18px;
      color: var(--muted);
      line-height: 1.45;
    }
    form {
      display: grid;
      gap: 14px;
    }
    label {
      display: grid;
      gap: 8px;
      color: var(--muted);
      font-weight: 780;
    }
    .helper-text {
      margin: 2px 0 0;
      color: #c8d4e3;
      font-size: 13px;
      line-height: 1.45;
    }
    .primary-action {
      width: 100%;
      margin-top: 2px;
    }
    .feature-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }
    .feature-card {
      min-height: 168px;
      padding: 20px;
      background: rgba(12, 18, 27, 0.88);
      transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
    }
    .feature-card:hover {
      transform: translateY(-2px);
      border-color: var(--line-strong);
      background: rgba(17, 26, 39, 0.94);
    }
    .feature-icon {
      display: grid;
      place-items: center;
      width: 42px;
      height: 42px;
      margin-bottom: 16px;
      border-radius: 8px;
      background: rgba(90, 169, 255, 0.14);
      color: var(--blue);
      font-size: 20px;
      font-weight: 950;
    }
    .feature-card:nth-child(2) .feature-icon {
      background: rgba(255, 159, 28, 0.15);
      color: var(--orange);
    }
    .feature-card:nth-child(3) .feature-icon {
      background: rgba(51, 209, 122, 0.13);
      color: var(--green);
    }
    .feature-card p {
      margin: 10px 0 0;
      color: var(--muted);
      line-height: 1.5;
    }
    .loading-panel {
      display: grid;
      gap: 22px;
      max-width: 760px;
      margin: 70px auto 0;
      padding: 28px;
      background: rgba(12, 18, 27, 0.96);
    }
    .loading-head {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: flex-start;
    }
    .loading-ring {
      width: 46px;
      height: 46px;
      border: 4px solid rgba(255, 159, 28, 0.20);
      border-top-color: var(--orange);
      border-radius: 50%;
      animation: spin 1s linear infinite;
      flex: 0 0 auto;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .stage-list {
      display: grid;
      gap: 10px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .stage-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 13px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #09101a;
      color: var(--muted);
      font-weight: 800;
    }
    .stage-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: var(--muted-2);
    }
    .stage-item.active {
      border-color: rgba(255, 159, 28, 0.65);
      color: var(--text);
      background: rgba(255, 159, 28, 0.10);
    }
    .stage-item.active .stage-dot {
      background: var(--orange);
      box-shadow: 0 0 0 7px rgba(255, 159, 28, 0.12);
      animation: pulse 1.2s ease-in-out infinite;
    }
    .stage-item.complete {
      color: #d9e3f1;
    }
    .stage-item.complete .stage-dot {
      background: var(--green);
    }
    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.15); }
    }
    .dashboard-shell {
      display: grid;
      gap: 18px;
    }
    .dashboard-header {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      align-items: end;
      padding: 22px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(12, 18, 27, 0.94);
    }
    .dashboard-title {
      margin-bottom: 7px;
      font-size: 32px;
      line-height: 1.1;
    }
    .dashboard-subtitle {
      margin: 0;
      color: var(--muted);
      line-height: 1.45;
    }
    .tab-bar {
      position: sticky;
      top: 0;
      z-index: 5;
      display: flex;
      gap: 8px;
      padding: 8px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(7, 10, 16, 0.94);
      backdrop-filter: blur(12px);
      overflow-x: auto;
    }
    .tab-button {
      flex: 0 0 auto;
      border: 1px solid transparent;
      background: transparent;
      color: var(--muted);
    }
    .tab-button.active {
      border-color: var(--line-strong);
      background: var(--panel-2);
      color: var(--text);
    }
    .tab-panel {
      display: grid;
      gap: 18px;
    }
    .tab-panel[hidden],
    [hidden] {
      display: none !important;
    }
    .section {
      overflow: hidden;
      background: rgba(16, 23, 34, 0.94);
    }
    .section-header {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      padding: 17px 19px;
      border-bottom: 1px solid var(--line);
      background: rgba(21, 31, 46, 0.92);
    }
    .section-body {
      padding: 19px;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 14px;
    }
    .metric-card {
      min-height: 126px;
      padding: 17px;
      background: rgba(11, 17, 26, 0.92);
      box-shadow: none;
    }
    .metric-card-wide { grid-column: span 2; }
    .metric-card-large { grid-column: span 2; }
    .metric-label,
    .detail-label,
    .coach-label,
    .debug-label,
    .small-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
    }
    .metric-label {
      margin-bottom: 9px;
    }
    .metric-value {
      margin-bottom: 0;
      color: var(--text);
      font-size: 27px;
      font-weight: 900;
      line-height: 1.1;
      overflow-wrap: anywhere;
    }
    .grade-value {
      font-size: 64px;
      line-height: 0.9;
    }
    .metric-copy {
      margin: 0;
      color: #d9e3f1;
      line-height: 1.52;
    }
    .takeaway-grid,
    .improve-grid {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 14px;
    }
    .focus-card,
    .takeaway-card {
      padding: 16px;
      background: rgba(11, 17, 26, 0.92);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: none;
    }
    .takeaway-card p,
    .focus-card p {
      margin: 9px 0 0;
      color: #d9e3f1;
      line-height: 1.48;
    }
    .review-controls {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }
    .filter-button {
      border: 1px solid var(--line);
      background: #0c1320;
      color: var(--text);
    }
    .filter-button.active {
      border-color: var(--orange);
      background: rgba(255, 159, 28, 0.14);
      color: var(--orange);
    }
    .round-list {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .round-review-card {
      display: grid;
      gap: 14px;
      padding: 16px;
      background: rgba(11, 17, 26, 0.92);
      box-shadow: none;
      transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
    }
    .round-review-card:hover {
      transform: translateY(-1px);
      border-color: var(--line-strong);
      background: rgba(13, 20, 30, 0.98);
    }
    .round-review-card[hidden] { display: none; }
    .round-card-header,
    .round-card-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }
    .round-card-title {
      justify-content: flex-start;
    }
    .round-explanation {
      margin: 0;
      color: #d9e3f1;
      line-height: 1.5;
    }
    .stat-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .stat-pill {
      display: inline-flex;
      gap: 6px;
      align-items: center;
      padding: 7px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #08101a;
      color: #d9e3f1;
      font-size: 13px;
      font-weight: 800;
    }
    .advanced-details,
    .dev-tools {
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: rgba(8, 14, 22, 0.92);
    }
    .advanced-details summary,
    .dev-tools summary {
      cursor: pointer;
      padding: 12px 14px;
      color: var(--muted);
      font-weight: 900;
      background: #0d1420;
    }
    .detail-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      padding: 14px;
    }
    .detail-item {
      padding: 11px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #0c131d;
    }
    .detail-label {
      margin-bottom: 5px;
    }
    .detail-value {
      margin-bottom: 0;
      color: var(--text);
      font-weight: 820;
      overflow-wrap: anywhere;
    }
    .replay-body {
      display: grid;
      gap: 16px;
      padding: 18px;
    }
    .replay-controls {
      display: grid;
      grid-template-columns: auto auto minmax(180px, 240px) auto minmax(260px, 1fr) auto;
      gap: 10px;
      align-items: center;
    }
    .timeline-wrap {
      display: grid;
      gap: 5px;
    }
    .timeline-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
    }
    .replay-layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 350px;
      gap: 16px;
      align-items: stretch;
    }
    .replay-stage {
      min-height: 660px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #05070c;
    }
    #replay-canvas {
      display: block;
      width: 100%;
      height: auto;
      max-height: 790px;
      aspect-ratio: 1 / 1;
      border-radius: 6px;
      background: #05070c;
    }
    .coach-panel {
      display: grid;
      align-content: start;
      gap: 14px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(11, 17, 26, 0.94);
    }
    .coach-block {
      display: grid;
      gap: 6px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--line);
    }
    .coach-block:last-child { border-bottom: 0; }
    .coach-value {
      color: var(--text);
      font-weight: 850;
      line-height: 1.35;
      overflow-wrap: anywhere;
    }
    .feed-list,
    .issue-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .feed-list li,
    .issue-list li {
      padding: 9px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #09101a;
      color: #d9e3f1;
      line-height: 1.35;
    }
    .improvement-hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 16px;
      align-items: stretch;
    }
    .focus-card.primary {
      background:
        linear-gradient(135deg, rgba(255, 159, 28, 0.16), rgba(11, 17, 26, 0.92) 45%),
        rgba(11, 17, 26, 0.92);
    }
    .debug-content {
      display: grid;
      gap: 16px;
      padding: 16px;
    }
    .debug-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }
    .debug-card {
      padding: 14px;
      background: rgba(11, 17, 26, 0.92);
      box-shadow: none;
    }
    .debug-label {
      margin-bottom: 7px;
    }
    .debug-value {
      margin: 0;
      color: #d9e3f1;
      font-weight: 800;
      overflow-wrap: anywhere;
    }
    .missing-list {
      display: grid;
      gap: 8px;
      margin: 0;
      padding: 0;
      list-style: none;
    }
    .missing-list li {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 10px 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #09101a;
      color: #d9e3f1;
    }
    pre {
      max-height: 520px;
      margin: 0;
      padding: 16px;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #05070c;
      color: #e5e7eb;
      white-space: pre-wrap;
      word-break: break-word;
    }
    .error-card {
      max-width: 780px;
      margin: 50px auto 0;
      padding: 26px;
      background: rgba(16, 23, 34, 0.96);
    }
    .error-card h2 {
      color: var(--red);
      margin-bottom: 10px;
    }
    .error-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 18px;
    }
    .badge { padding: 5px 9px; }
    .badge-high {
      background: rgba(255, 77, 77, 0.15);
      color: var(--red);
    }
    .badge-medium {
      background: rgba(255, 159, 28, 0.16);
      color: var(--orange);
    }
    .badge-low {
      background: rgba(51, 209, 122, 0.14);
      color: var(--green);
    }
    .badge-neutral {
      background: rgba(90, 169, 255, 0.14);
      color: var(--blue);
    }
    .muted { color: var(--muted); }
    .risk-high { color: var(--red); }
    .risk-medium { color: var(--orange); }
    .risk-low { color: var(--green); }
    .hidden-count {
      margin-top: 12px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 750;
    }
    @media (max-width: 1180px) {
      .hero,
      .improvement-hero { grid-template-columns: 1fr; }
      .hero { min-height: 0; }
      .upload-panel { max-width: 560px; }
      .summary-grid,
      .takeaway-grid,
      .improve-grid,
      .debug-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .metric-card-wide,
      .metric-card-large { grid-column: span 1; }
      .detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .replay-layout { grid-template-columns: 1fr; }
      .replay-controls { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .timeline-wrap { grid-column: 1 / -1; }
    }
    @media (max-width: 760px) {
      main { padding: 18px 12px 38px; }
      .product-topbar,
      .dashboard-header { display: grid; }
      .hero { padding: 22px; }
      .feature-grid,
      .summary-grid,
      .takeaway-grid,
      .improve-grid,
      .debug-grid,
      .detail-grid,
      .round-list,
      .replay-controls { grid-template-columns: 1fr; }
      .grade-value { font-size: 52px; }
      .replay-stage { min-height: 360px; }
      .dashboard-title { font-size: 28px; }
    }
  </style>
</head>
<body>
  <main>
    <div class="product-topbar">
      <div class="brand-lockup">
        <span class="brand-mark">CS</span>
        <span>CS Demo Coach AI</span>
      </div>
      <span class="status-pill">Local demo analysis</span>
    </div>

    <section id="landing" class="landing">
      <section class="hero">
        <div class="hero-copy">
          <p class="eyebrow">Counter-Strike 2 Coaching</p>
          <h1>CS Demo Coach AI</h1>
          <p class="subtitle">Upload a CS2 demo and get a round-by-round improvement report.</p>
          <div class="hero-proof">
            <span>Real .dem parsing</span>
            <span>Round review</span>
            <span>Replay-ready insights</span>
          </div>
        </div>

        <aside class="upload-panel">
          <h2>Analyze Your Demo</h2>
          <p class="panel-copy">Choose a match demo and enter the exact in-game player name you want reviewed.</p>
          <form id="analyze-form">
            <label>
              Demo file (.dem)
              <input id="file" name="file" type="file" accept=".dem" required>
            </label>
            <label>
              Player name
              <input id="player_name" name="player_name" type="text" placeholder="Exact in-demo player name" required>
            </label>
            <button id="submit" class="primary-action" type="submit">Analyze Demo</button>
            <p class="helper-text">Your demo is analyzed by the server. Large demos may take 1-3 minutes to parse.</p>
          </form>
        </aside>
      </section>

      <section class="feature-grid" aria-label="Product features">
        <article class="feature-card">
          <div class="feature-icon">M</div>
          <h3>Match Report</h3>
          <p>Get a readable summary of strong rounds, weak rounds, recurring mistakes, and the most important takeaway.</p>
        </article>
        <article class="feature-card">
          <div class="feature-icon">R</div>
          <h3>Round Replay</h3>
          <p>Review movement, kills, and utility events on a real map view when the demo exposes replay tick data.</p>
        </article>
        <article class="feature-card">
          <div class="feature-icon">I</div>
          <h3>Improvement Plan</h3>
          <p>Turn repeated round issues into practical focus areas for your next match.</p>
        </article>
      </section>
    </section>

    <section id="loading" class="loading-panel" hidden>
      <div class="loading-head">
        <div>
          <p class="eyebrow">Analysis Running</p>
          <h2>Building your coaching report</h2>
          <p class="panel-copy">Large demos may take 1-3 minutes to parse. Keep this tab open while the server works.</p>
        </div>
        <div class="loading-ring" aria-hidden="true"></div>
      </div>
      <ol id="stage-list" class="stage-list">
        <li class="stage-item" data-stage="0"><span class="stage-dot"></span> Uploading demo</li>
        <li class="stage-item" data-stage="1"><span class="stage-dot"></span> Parsing replay</li>
        <li class="stage-item" data-stage="2"><span class="stage-dot"></span> Extracting rounds</li>
        <li class="stage-item" data-stage="3"><span class="stage-dot"></span> Running model</li>
        <li class="stage-item" data-stage="4"><span class="stage-dot"></span> Building report</li>
      </ol>
    </section>

    <div id="report" class="dashboard-shell" hidden></div>
  </main>

  <script>
    const landing = document.getElementById("landing");
    const loading = document.getElementById("loading");
    const form = document.getElementById("analyze-form");
    const button = document.getElementById("submit");
    const report = document.getElementById("report");
    const loadingStages = [...document.querySelectorAll(".stage-item")];

    const replayState = {
      analysis: null,
      modelInfo: null,
      replay: null,
      roundIndex: 0,
      currentTick: 0,
      playing: false,
      speed: 1,
      lastFrameTime: null,
      animationFrame: null,
      mapImage: null,
      mapImageLoaded: false,
      mapImageError: false,
      pendingReplayRound: null,
      activeTab: "match-report",
    };

    let loadingTimer = null;
    let loadingStageIndex = 0;

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function numeric(value) {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : null;
    }

    function hasValue(value) {
      return value !== null && value !== undefined && value !== "";
    }

    function pct(value) {
      const parsed = numeric(value);
      return parsed === null ? "Not available" : `${Math.round(parsed * 100)}%`;
    }

    function confidence(round) {
      return numeric(round?.bad_round_probability) ?? numeric(round?.risk_score) ?? 0;
    }

    function concernClass(value) {
      const parsed = numeric(value);
      if (parsed >= 0.70) return "risk-high";
      if (parsed >= 0.45) return "risk-medium";
      return "risk-low";
    }

    function reviewResult(round) {
      const value = confidence(round);
      if (round?.bad_round_prediction === 1 || value >= 0.70) return "High Risk";
      if (value >= 0.45) return "Needs Review";
      return "Good Round";
    }

    function resultBadge(round) {
      const result = reviewResult(round);
      if (result === "High Risk") return '<span class="badge badge-high">High Risk</span>';
      if (result === "Needs Review") return '<span class="badge badge-medium">Needs Review</span>';
      return '<span class="badge badge-low">Good Round</span>';
    }

    function display(value, fallback = "Not available") {
      if (!hasValue(value)) return fallback;
      if (typeof value === "boolean") return value ? "Yes" : "No";
      return value;
    }

    function raw(round, key) {
      return round?.raw_features?.[key];
    }

    function issueList(issues) {
      if (!Array.isArray(issues) || issues.length === 0) return ["No major issue detected"];
      return issues;
    }

    function realIssues(round) {
      return issueList(round?.detected_issues).filter((issue) => issue !== "No major issue detected");
    }

    function countIssues(rounds) {
      const counts = new Map();
      for (const round of rounds) {
        for (const issue of realIssues(round)) {
          counts.set(issue, (counts.get(issue) || 0) + 1);
        }
      }
      return [...counts.entries()].sort((a, b) => b[1] - a[1]);
    }

    function sentenceJoin(items) {
      if (items.length === 0) return "";
      if (items.length === 1) return items[0];
      return `${items.slice(0, -1).join(", ")} and ${items.at(-1)}`;
    }

    function roundTitle(round) {
      return hasValue(round?.round) ? `Round ${round.round}` : "Unknown round";
    }

    function bestWorst(rounds) {
      const sorted = [...rounds].sort((a, b) => confidence(b) - confidence(a));
      return { worst: sorted[0], best: sorted.at(-1), sorted };
    }

    function avg(values) {
      const filtered = values.map(numeric).filter((value) => value !== null);
      if (filtered.length === 0) return null;
      return filtered.reduce((sum, value) => sum + value, 0) / filtered.length;
    }

    function performanceGrade(overallConcern) {
      const value = numeric(overallConcern);
      if (value === null) return "C";
      if (value <= 0.25) return "A";
      if (value <= 0.45) return "B";
      if (value <= 0.65) return "C";
      return "D";
    }

    function gradeClass(grade) {
      if (grade === "A" || grade === "B") return "risk-low";
      if (grade === "C") return "risk-medium";
      return "risk-high";
    }

    function mainWeakness(rounds) {
      const counts = countIssues(rounds);
      if (counts.length === 0) return "No repeated high-concern pattern stood out in this demo.";
      const top = counts.slice(0, 2).map(([issue]) => issue.toLowerCase());
      return `Your highest-concern pattern was ${sentenceJoin(top)}.`;
    }

    function biggestStrength(rounds) {
      const survived = rounds.filter((round) => raw(round, "survived_round") === true).length;
      const utilityRounds = rounds.filter((round) => (numeric(raw(round, "utility_count")) ?? 0) > 0).length;
      const totalKills = rounds.reduce((sum, round) => sum + (numeric(raw(round, "kills")) ?? 0), 0);
      const totalDeaths = rounds.reduce((sum, round) => sum + (numeric(raw(round, "deaths")) ?? 0), 0);
      const avgDamage = avg(rounds.map((round) => raw(round, "damage_dealt")));

      if (rounds.length === 0) return "No rounds were available to summarize.";
      if (survived >= Math.ceil(rounds.length * 0.45)) return `You survived ${survived} of ${rounds.length} reviewed rounds.`;
      if (utilityRounds >= Math.ceil(rounds.length * 0.70)) return `You used utility in ${utilityRounds} of ${rounds.length} reviewed rounds.`;
      if (avgDamage !== null && avgDamage >= 70) return `You averaged ${avgDamage.toFixed(0)} damage per reviewed round.`;
      if (totalKills > totalDeaths) return `You finished with more kills (${totalKills}) than deaths (${totalDeaths}) in reviewed rounds.`;
      return "Your strongest rounds were the low-concern rounds highlighted in the Rounds tab.";
    }

    function roundWonText(round) {
      const won = raw(round, "round_win");
      if (won === true) return "Round won";
      if (won === false) return "Round lost";
      return null;
    }

    function plainEnglishRound(round) {
      const issues = realIssues(round);
      if (issues.length) return `Needs attention because of ${sentenceJoin(issues.map((item) => item.toLowerCase()))}.`;
      const kills = numeric(raw(round, "kills")) ?? 0;
      const deaths = numeric(raw(round, "deaths")) ?? 0;
      const damage = numeric(raw(round, "damage_dealt")) ?? 0;
      if (deaths === 0 && (kills > 0 || damage > 0)) return "Strong round: you stayed alive and created impact.";
      if (deaths === 0) return "Stable round with no major concern detected.";
      return "Acceptable round with no repeated concern detected.";
    }

    function keyTakeaways(rounds) {
      const issueCounts = countIssues(rounds);
      const { worst, best } = bestWorst(rounds);
      const utilityValues = rounds.map((round) => raw(round, "utility_count")).map(numeric).filter((value) => value !== null);
      const avgUtility = avg(utilityValues);
      const zeroUtility = utilityValues.filter((value) => value === 0).length;
      const deaths = rounds.reduce((sum, round) => sum + (numeric(raw(round, "deaths")) || 0), 0);
      const kills = rounds.reduce((sum, round) => sum + (numeric(raw(round, "kills")) || 0), 0);
      const survived = rounds.filter((round) => raw(round, "survived_round") === true).length;

      return [
        ["Most common mistake", issueCounts.length ? `${issueCounts[0][0]} appeared in ${issueCounts[0][1]} rounds.` : "No repeated mistake stood out."],
        ["Worst round", worst ? `${roundTitle(worst)} had the highest review confidence at ${pct(confidence(worst))}.` : "No round data available."],
        ["Best round", best ? `${roundTitle(best)} had the lowest concern level at ${pct(confidence(best))}.` : "No round data available."],
        ["Utility usage", avgUtility !== null ? `You averaged ${avgUtility.toFixed(1)} utility actions per round; ${zeroUtility} rounds had zero utility.` : "Utility data was not available."],
        ["Survival and impact", `You recorded ${kills} kills, ${deaths} deaths, and survived ${survived} of ${rounds.length} reviewed rounds.`],
      ];
    }

    function improvementFocus(rounds) {
      const counts = countIssues(rounds);
      if (counts.length === 0) return "No single repeated mistake dominated this demo. Review your highest-concern rounds and look for shared timing or positioning choices.";

      const top = counts[0][0].toLowerCase();
      const second = counts[1]?.[0]?.toLowerCase() || "";
      if (top.includes("died without a kill")) {
        return "You were most often punished when dying without impact. Focus on taking fights that can be traded, and use utility before solo contact.";
      }
      if (top.includes("no utility")) {
        return "Your recurring issue was low utility usage. Focus on throwing one useful grenade before taking early fights.";
      }
      if (top.includes("first death")) {
        return "You were often involved in the first death of the round. Focus on safer opening routes and waiting for teammate support.";
      }
      if (top.includes("no damage")) {
        return "Several reviewed rounds had no damage or kills recorded. Focus on reaching earlier impact positions and clearing common angles with intent.";
      }
      if (second) {
        return `Your top repeated issues were ${top} and ${second}. Start by reviewing those rounds and planning one safer decision before first contact.`;
      }
      return `Your top repeated issue was ${top}. Review those rounds and choose one habit to fix in the next match.`;
    }

    function detailItems(round) {
      const fields = [
        ["Kills before death", raw(round, "kills_before_death")],
        ["Damage before death", raw(round, "damage_before_death")],
        ["Opening kill", raw(round, "opening_kill")],
        ["Opening death", raw(round, "opening_death")],
        ["Clutch situation", raw(round, "clutch_situation")],
        ["Utility before death", raw(round, "utility_used_before_death")],
        ["Round result", roundWonText(round)],
        ["Side", raw(round, "side")],
        ["Team", raw(round, "team")],
        ["Team alive when died", raw(round, "team_alive_when_player_died")],
        ["Enemies alive when died", raw(round, "enemies_alive_when_player_died")],
        ["Death tick", raw(round, "death_tick")],
      ];

      const items = fields
        .filter(([, value]) => hasValue(value))
        .map(([label, value]) => `
          <div class="detail-item">
            <p class="detail-label">${escapeHtml(label)}</p>
            <p class="detail-value">${escapeHtml(display(value))}</p>
          </div>
        `).join("");

      const issueItems = `
        <div class="detail-item">
          <p class="detail-label">Detected issues</p>
          <p class="detail-value">${escapeHtml(issueList(round.detected_issues).join(", "))}</p>
        </div>
      `;
      return items + issueItems;
    }

    function suggestionForIssue(issue) {
      const value = String(issue).toLowerCase();
      if (value.includes("no utility")) return "Use one purposeful grenade before taking first contact.";
      if (value.includes("died without a kill")) return "Play closer to a trade partner or choose a safer opening angle.";
      if (value.includes("first death")) return "Delay first contact unless you have utility or teammate support.";
      if (value.includes("no damage")) return "Prioritize earlier impact by pre-aiming common contact points.";
      return "Review the timing and pathing around the flagged moment.";
    }

    function statPills(round, includeConfidence = false) {
      const stats = [
        ["Kills", display(raw(round, "kills"), "0")],
        ["Deaths", display(raw(round, "deaths"), "0")],
        ["Damage", display(raw(round, "damage_dealt"), "0")],
        ["Utility", display(raw(round, "utility_count"), "0")],
      ];
      if (includeConfidence) stats.push(["Confidence", pct(confidence(round))]);
      return stats.map(([label, value]) => `<span class="stat-pill"><span class="muted">${escapeHtml(label)}:</span> ${escapeHtml(value)}</span>`).join("");
    }

    function setLoadingStage(index) {
      loadingStageIndex = Math.max(0, Math.min(loadingStages.length - 1, index));
      for (const item of loadingStages) {
        const stage = Number(item.dataset.stage);
        item.classList.toggle("complete", stage < loadingStageIndex);
        item.classList.toggle("active", stage === loadingStageIndex);
      }
    }

    function startLoading() {
      clearInterval(loadingTimer);
      setLoadingStage(0);
      loadingTimer = setInterval(() => {
        if (loadingStageIndex < loadingStages.length - 1) setLoadingStage(loadingStageIndex + 1);
      }, 9000);
    }

    function stopLoading() {
      clearInterval(loadingTimer);
      loadingTimer = null;
      setLoadingStage(loadingStages.length - 1);
    }

    function resetToLanding() {
      report.hidden = true;
      loading.hidden = true;
      landing.hidden = false;
      replayState.playing = false;
      if (replayState.animationFrame) cancelAnimationFrame(replayState.animationFrame);
    }

    function showError(message) {
      stopLoading();
      landing.hidden = true;
      loading.hidden = true;
      report.hidden = false;
      report.className = "dashboard-shell";
      report.innerHTML = `
        <article class="error-card">
          <p class="eyebrow">Analysis Failed</p>
          <h2>We could not analyze this demo.</h2>
          <p class="metric-copy">Common causes include an invalid .dem file, unsupported demo format, player name not found, or a parser error while reading the replay.</p>
          <ul class="issue-list" style="margin-top: 16px;">
            <li>Check that the uploaded file ends in .dem.</li>
            <li>Make sure the player name matches the in-demo name.</li>
            <li>Try a different demo if this one was recorded in an unsupported format.</li>
          </ul>
          <details class="advanced-details" style="margin-top: 16px;">
            <summary>Technical error</summary>
            <pre>${escapeHtml(message || "No technical detail returned.")}</pre>
          </details>
          <div class="error-actions">
            <button id="try-again" type="button">Try Another Demo</button>
          </div>
        </article>
      `;
      document.getElementById("try-again").addEventListener("click", resetToLanding);
    }

    async function readResponsePayload(response) {
      const text = await response.text();
      if (!text) return {};

      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        try {
          return JSON.parse(text);
        } catch (error) {
          return { detail: `Server returned invalid JSON: ${String(error)}`, raw_response: text };
        }
      }

      try {
        return JSON.parse(text);
      } catch {
        return { detail: text };
      }
    }

    function errorMessageFromPayload(payload, fallback) {
      if (typeof payload?.detail === "string") return payload.detail;
      if (Array.isArray(payload?.detail)) return payload.detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
      if (typeof payload?.error === "string") return payload.error;
      if (typeof payload?.message === "string") return payload.message;
      return fallback;
    }

    function matchReportHtml(payload, rounds) {
      const grade = performanceGrade(payload.overall_risk_score);
      const strongRounds = rounds.filter((round) => reviewResult(round) === "Good Round").length;
      const weakRounds = rounds.filter((round) => reviewResult(round) === "High Risk").length;
      const takeaways = keyTakeaways(rounds);

      return `
        <section class="section">
          <div class="section-header">
            <h2>Game Summary</h2>
            <span class="muted">Round-by-round coaching report</span>
          </div>
          <div class="section-body">
            <div class="summary-grid">
              <div class="metric-card metric-card-large">
                <p class="metric-label">Overall performance grade</p>
                <p class="metric-value grade-value ${gradeClass(grade)}">${escapeHtml(grade)}</p>
              </div>
              <div class="metric-card metric-card-wide">
                <p class="metric-label">Player</p>
                <p class="metric-value">${escapeHtml(payload.player)}</p>
              </div>
              <div class="metric-card">
                <p class="metric-label">Rounds reviewed</p>
                <p class="metric-value">${escapeHtml(payload.rounds_analyzed)}</p>
              </div>
              <div class="metric-card">
                <p class="metric-label">Strong rounds</p>
                <p class="metric-value risk-low">${strongRounds}</p>
              </div>
              <div class="metric-card">
                <p class="metric-label">Weak rounds</p>
                <p class="metric-value risk-high">${weakRounds}</p>
              </div>
              <div class="metric-card metric-card-wide">
                <p class="metric-label">Main weakness</p>
                <p class="metric-copy">${escapeHtml(mainWeakness(rounds))}</p>
              </div>
              <div class="metric-card metric-card-wide">
                <p class="metric-label">Biggest strength</p>
                <p class="metric-copy">${escapeHtml(biggestStrength(rounds))}</p>
              </div>
            </div>
          </div>
        </section>
        <section class="section">
          <div class="section-header">
            <h2>Key Takeaways</h2>
            <span class="muted">Generated from round stats</span>
          </div>
          <div class="section-body">
            <div class="takeaway-grid">
              ${takeaways.map(([title, copy]) => `
                <article class="takeaway-card">
                  <p class="small-label">${escapeHtml(title)}</p>
                  <p>${escapeHtml(copy)}</p>
                </article>
              `).join("")}
            </div>
          </div>
        </section>
      `;
    }

    function roundCardHtml(round) {
      const side = String(raw(round, "side") || "").toLowerCase();
      const won = roundWonText(round);
      const dataFilter = [
        reviewResult(round) === "High Risk" ? "high" : "",
        reviewResult(round) === "Good Round" ? "good" : "",
        side === "t" ? "t" : "",
        side === "ct" ? "ct" : "",
      ].filter(Boolean).join(" ");

      return `
        <article class="round-review-card" data-filter="${escapeHtml(dataFilter)}">
          <div class="round-card-header">
            <div class="round-card-title">
              <h3>${escapeHtml(roundTitle(round))}</h3>
              ${resultBadge(round)}
              ${won ? `<span class="badge badge-neutral">${escapeHtml(won)}</span>` : ""}
            </div>
            <span class="${concernClass(confidence(round))}">Confidence ${pct(confidence(round))}</span>
          </div>
          <div class="stat-row">${statPills(round)}</div>
          <p class="round-explanation">${escapeHtml(plainEnglishRound(round))}</p>
          <div class="stat-row">
            <button class="secondary-button view-replay-button" type="button" data-round="${escapeHtml(round.round)}">View Replay</button>
          </div>
          <details class="advanced-details">
            <summary>Advanced stats</summary>
            <div class="detail-grid">${detailItems(round)}</div>
          </details>
        </article>
      `;
    }

    function roundsHtml(rounds) {
      return `
        <section class="section">
          <div class="section-header">
            <h2>Rounds</h2>
            <span class="muted">Clean review cards</span>
          </div>
          <div class="section-body">
            <div class="review-controls" aria-label="Round filters">
              <button class="filter-button active" type="button" data-filter="all">All</button>
              <button class="filter-button" type="button" data-filter="high">High Risk</button>
              <button class="filter-button" type="button" data-filter="good">Good Rounds</button>
              <button class="filter-button" type="button" data-filter="t">T Side</button>
              <button class="filter-button" type="button" data-filter="ct">CT Side</button>
            </div>
            <div id="round-list" class="round-list">
              ${rounds.map(roundCardHtml).join("")}
            </div>
            <div id="round-filter-count" class="hidden-count"></div>
          </div>
        </section>
      `;
    }

    function renderReplayPanel() {
      return `
        <section class="section" id="replay-section">
          <div class="section-header">
            <h2>Replay</h2>
            <span class="muted" id="replay-status">Waiting for replay data...</span>
          </div>
          <div class="replay-body">
            <div class="replay-controls">
              <button class="secondary-button" id="replay-prev" type="button">Previous Round</button>
              <button id="replay-play" type="button">Play</button>
              <select id="replay-round" aria-label="Replay round"></select>
              <select id="replay-speed" aria-label="Playback speed">
                <option value="0.5">0.5x</option>
                <option value="1" selected>1x</option>
                <option value="2">2x</option>
                <option value="4">4x</option>
              </select>
              <div class="timeline-wrap">
                <input id="replay-timeline" type="range" min="0" max="0" value="0" step="1">
                <span class="timeline-label" id="replay-tick-label">Tick: Not available</span>
              </div>
              <button class="secondary-button" id="replay-next" type="button">Next Round</button>
            </div>
            <div class="replay-layout">
              <div class="replay-stage">
                <canvas id="replay-canvas" width="1024" height="1024"></canvas>
              </div>
              <aside class="coach-panel">
                <div id="coach-summary">
                  <div class="coach-block">
                    <span class="coach-label">Round summary</span>
                    <span class="coach-value">Replay data is loading.</span>
                  </div>
                </div>
                <div class="coach-block">
                  <span class="coach-label">Kill Feed</span>
                  <ul class="feed-list" id="kill-feed"><li>No kills yet.</li></ul>
                </div>
                <div class="coach-block">
                  <span class="coach-label">Utility Feed</span>
                  <ul class="feed-list" id="utility-feed"><li>No utility yet.</li></ul>
                </div>
              </aside>
            </div>
          </div>
        </section>
      `;
    }

    function improveHtml(rounds) {
      const issueCounts = countIssues(rounds);
      const topIssues = issueCounts.slice(0, 3);
      const zeroUtility = rounds.filter((round) => (numeric(raw(round, "utility_count")) ?? 0) === 0).length;
      const highConcern = rounds.filter((round) => reviewResult(round) === "High Risk").length;
      const survived = rounds.filter((round) => raw(round, "survived_round") === true).length;

      return `
        <section class="section">
          <div class="section-header">
            <h2>Improve</h2>
            <span class="muted">Focus plan for the next match</span>
          </div>
          <div class="section-body">
            <div class="improvement-hero">
              <article class="focus-card primary">
                <p class="small-label">Recommended focus</p>
                <p>${escapeHtml(improvementFocus(rounds))}</p>
              </article>
              <article class="focus-card">
                <p class="small-label">Report snapshot</p>
                <p>${highConcern} high-risk rounds, ${zeroUtility} zero-utility rounds, survived ${survived} of ${rounds.length} reviewed rounds.</p>
              </article>
            </div>
            <div class="improve-grid" style="margin-top: 14px;">
              ${(topIssues.length ? topIssues : [["No repeated issue detected", 0]]).map(([issue, count]) => `
                <article class="focus-card">
                  <p class="small-label">${escapeHtml(count ? `${count} rounds` : "Summary")}</p>
                  <h3>${escapeHtml(issue)}</h3>
                  <p>${escapeHtml(count ? suggestionForIssue(issue) : "Use the Rounds tab to study your best and weakest rounds in context.")}</p>
                </article>
              `).join("")}
            </div>
          </div>
        </section>
      `;
    }

    function modelInfoHtml(modelInfo) {
      if (!modelInfo) {
        return `
          <div class="debug-card">
            <p class="debug-label">Model Info</p>
            <p class="debug-value">Could not load /model-info.</p>
          </div>
        `;
      }
      const columns = Array.isArray(modelInfo.feature_columns) ? modelInfo.feature_columns : [];
      const cards = [
        ["model_status", modelInfo.model_status],
        ["model_exists", modelInfo.model_exists],
        ["model_type", modelInfo.model_type],
        ["last_modified", modelInfo.last_modified],
        ["feature_columns", columns.length ? `${columns.length} columns` : null],
        ["model_path", modelInfo.model_path],
      ].filter(([, value]) => hasValue(value));

      return cards.map(([label, value]) => `
        <div class="debug-card">
          <p class="debug-label">${escapeHtml(label)}</p>
          <p class="debug-value">${escapeHtml(display(value))}</p>
        </div>
      `).join("") + `
        <details class="advanced-details">
          <summary>Model feature columns</summary>
          <pre>${escapeHtml(columns.join("\\n") || "No feature columns returned.")}</pre>
        </details>
      `;
    }

    function missingFeaturesHtml(summary) {
      const entries = Object.entries(summary || {}).filter(([, count]) => Number(count) > 0);
      if (entries.length === 0) return '<p class="muted">No missing features were reported.</p>';
      return `<ul class="missing-list">${entries.map(([name, count]) => `
        <li><span>${escapeHtml(name)}</span><strong>${escapeHtml(count)}</strong></li>
      `).join("")}</ul>`;
    }

    function developerToolsHtml(payload, modelInfo) {
      return `
        <details class="dev-tools">
          <summary>Developer Tools</summary>
          <div class="debug-content">
            <div class="debug-grid">
              ${modelInfoHtml(modelInfo)}
            </div>
            <section>
              <p class="debug-label">Missing features summary</p>
              ${missingFeaturesHtml(payload.missing_features_summary)}
            </section>
            <section>
              <p class="debug-label">Raw JSON</p>
              <pre id="raw-json">Waiting for replay data...</pre>
            </section>
          </div>
        </details>
      `;
    }

    function setRawJson(payload) {
      const rawJson = document.getElementById("raw-json");
      if (rawJson) rawJson.textContent = JSON.stringify(payload, null, 2);
    }

    function setupTabs() {
      const buttons = [...report.querySelectorAll(".tab-button")];
      const panels = [...report.querySelectorAll(".tab-panel")];

      function activate(tabName) {
        replayState.activeTab = tabName;
        for (const button of buttons) {
          const active = button.dataset.tab === tabName;
          button.classList.toggle("active", active);
          button.setAttribute("aria-selected", String(active));
        }
        for (const panel of panels) {
          panel.hidden = panel.dataset.panel !== tabName;
        }
        if (tabName === "replay") drawReplay();
      }

      window.activateCoachTab = activate;
      for (const button of buttons) {
        button.addEventListener("click", () => activate(button.dataset.tab));
      }
      activate("match-report");
    }

    function setupRoundFilters() {
      const buttons = [...document.querySelectorAll(".filter-button")];
      const cards = [...document.querySelectorAll(".round-review-card")];
      const count = document.getElementById("round-filter-count");

      function applyFilter(filter) {
        let shown = 0;
        for (const card of cards) {
          const visible = filter === "all" || String(card.dataset.filter || "").split(" ").includes(filter);
          card.hidden = !visible;
          if (visible) shown += 1;
        }
        for (const button of buttons) {
          button.classList.toggle("active", button.dataset.filter === filter);
        }
        if (count) count.textContent = `${shown} of ${cards.length} rounds shown`;
      }

      for (const button of buttons) {
        button.addEventListener("click", () => applyFilter(button.dataset.filter));
      }
      applyFilter("all");
    }

    function setupReplayButtons() {
      for (const button of document.querySelectorAll(".view-replay-button")) {
        button.addEventListener("click", () => viewReplayRound(button.dataset.round));
      }
    }

    function viewReplayRound(roundNumber) {
      replayState.pendingReplayRound = roundNumber;
      if (typeof window.activateCoachTab === "function") window.activateCoachTab("replay");
      const rounds = replayState.replay?.rounds || [];
      const index = rounds.findIndex((round) => String(round.round_number) === String(roundNumber));
      if (index >= 0) {
        setReplayRound(index);
      } else {
        setReplayStatus("Replay data is still loading for this demo.");
      }
    }

    function renderReport(payload, modelInfo) {
      const rounds = payload.round_reports || [];
      replayState.analysis = payload;
      replayState.modelInfo = modelInfo;

      report.hidden = false;
      report.className = "dashboard-shell";
      report.innerHTML = `
        <section class="dashboard-header">
          <div>
            <p class="eyebrow">Analysis Complete</p>
            <h2 class="dashboard-title">${escapeHtml(payload.player)} Match Review</h2>
            <p class="dashboard-subtitle">${escapeHtml(payload.rounds_analyzed)} rounds reviewed from real demo data.</p>
          </div>
          <button class="ghost-button" id="analyze-another" type="button">Analyze Another Demo</button>
        </section>
        <nav class="tab-bar" aria-label="Coaching report tabs">
          <button type="button" class="tab-button active" data-tab="match-report" aria-selected="true">Match Report</button>
          <button type="button" class="tab-button" data-tab="rounds" aria-selected="false">Rounds</button>
          <button type="button" class="tab-button" data-tab="replay" aria-selected="false">Replay</button>
          <button type="button" class="tab-button" data-tab="improve" aria-selected="false">Improve</button>
        </nav>
        <section class="tab-panel" data-panel="match-report">
          ${matchReportHtml(payload, rounds)}
        </section>
        <section class="tab-panel" data-panel="rounds" hidden>
          ${roundsHtml(rounds)}
        </section>
        <section class="tab-panel" data-panel="replay" hidden>
          ${renderReplayPanel()}
        </section>
        <section class="tab-panel" data-panel="improve" hidden>
          ${improveHtml(rounds)}
        </section>
        ${developerToolsHtml(payload, modelInfo)}
      `;

      document.getElementById("analyze-another").addEventListener("click", resetToLanding);
      setupTabs();
      setupRoundFilters();
      setupReplayButtons();
      drawReplayMessage("Replay data is loading from the real demo...");
      setRawJson({ analysis: payload, model_info: modelInfo, replay: replayState.replay });
    }

    function drawReplayMessage(message) {
      const canvas = document.getElementById("replay-canvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#05070c";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#edf3ff";
      ctx.font = "700 24px system-ui, sans-serif";
      ctx.fillText(message, 44, 72);
    }

    function currentReplayRound() {
      return replayState.replay?.rounds?.[replayState.roundIndex] || null;
    }

    function analysisRound(roundNumber) {
      return replayState.analysis?.round_reports?.find((round) => String(round.round) === String(roundNumber)) || null;
    }

    function setReplayStatus(text) {
      const status = document.getElementById("replay-status");
      if (status) status.textContent = text;
    }

    function loadReplayMapImage(imageUrl) {
      replayState.mapImageLoaded = false;
      replayState.mapImageError = false;
      replayState.mapImage = new Image();
      replayState.mapImage.onload = () => {
        replayState.mapImageLoaded = true;
        drawReplay();
      };
      replayState.mapImage.onerror = () => {
        replayState.mapImageError = true;
        drawReplay();
      };
      replayState.mapImage.src = imageUrl;
    }

    function setupReplay(replayPayload) {
      replayState.replay = replayPayload;
      replayState.roundIndex = 0;
      replayState.playing = false;
      replayState.lastFrameTime = null;

      if (!replayPayload?.replay_available) {
        setReplayStatus(replayPayload?.reason || "Replay data unavailable.");
        drawReplayMessage(replayPayload?.reason || "Replay data unavailable.");
        updateCoachPanel(null);
        return;
      }

      const roundSelect = document.getElementById("replay-round");
      if (!roundSelect) return;
      roundSelect.innerHTML = replayPayload.rounds.map((round, index) => `
        <option value="${index}">Round ${escapeHtml(round.round_number)}</option>
      `).join("");
      roundSelect.addEventListener("change", () => setReplayRound(Number(roundSelect.value)));

      document.getElementById("replay-prev").addEventListener("click", () => setReplayRound(replayState.roundIndex - 1));
      document.getElementById("replay-next").addEventListener("click", () => setReplayRound(replayState.roundIndex + 1));
      document.getElementById("replay-play").addEventListener("click", toggleReplay);
      document.getElementById("replay-speed").addEventListener("change", (event) => {
        replayState.speed = Number(event.target.value) || 1;
      });
      document.getElementById("replay-timeline").addEventListener("input", (event) => {
        replayState.currentTick = Number(event.target.value);
        replayState.playing = false;
        updatePlayButton();
        drawReplay();
      });

      const image = replayPayload.map_config?.image;
      if (image) loadReplayMapImage(image);
      setReplayRound(0);
      if (replayState.pendingReplayRound) {
        const index = replayPayload.rounds.findIndex((round) => String(round.round_number) === String(replayState.pendingReplayRound));
        if (index >= 0) setReplayRound(index);
        replayState.pendingReplayRound = null;
      }
      setReplayStatus(`${replayPayload.map_name} replay data loaded.`);
    }

    function setReplayRound(index) {
      const rounds = replayState.replay?.rounds || [];
      if (!rounds.length) return;
      replayState.roundIndex = Math.max(0, Math.min(rounds.length - 1, index));
      replayState.playing = false;
      replayState.lastFrameTime = null;
      const round = currentReplayRound();
      replayState.currentTick = Number(round.tick_start ?? firstRoundTick(round));

      const select = document.getElementById("replay-round");
      const timeline = document.getElementById("replay-timeline");
      if (select) select.value = String(replayState.roundIndex);
      if (timeline) {
        timeline.min = String(round.tick_start ?? firstRoundTick(round));
        timeline.max = String(round.tick_end ?? lastRoundTick(round));
        timeline.value = String(replayState.currentTick);
      }
      document.getElementById("replay-prev").disabled = replayState.roundIndex === 0;
      document.getElementById("replay-next").disabled = replayState.roundIndex === rounds.length - 1;
      updatePlayButton();
      updateCoachPanel(round);
      drawReplay();
    }

    function firstRoundTick(round) {
      const ticks = round.players.flatMap((player) => player.positions.map((position) => position.tick));
      return ticks.length ? Math.min(...ticks) : 0;
    }

    function lastRoundTick(round) {
      const ticks = round.players.flatMap((player) => player.positions.map((position) => position.tick));
      return ticks.length ? Math.max(...ticks) : firstRoundTick(round);
    }

    function updatePlayButton() {
      const button = document.getElementById("replay-play");
      if (button) button.textContent = replayState.playing ? "Pause" : "Play";
    }

    function toggleReplay() {
      replayState.playing = !replayState.playing;
      replayState.lastFrameTime = null;
      updatePlayButton();
      if (replayState.playing) {
        replayState.animationFrame = requestAnimationFrame(stepReplay);
      }
    }

    function stepReplay(timestamp) {
      if (!replayState.playing) return;
      const round = currentReplayRound();
      if (!round) return;
      if (replayState.lastFrameTime === null) replayState.lastFrameTime = timestamp;
      const deltaSeconds = (timestamp - replayState.lastFrameTime) / 1000;
      replayState.lastFrameTime = timestamp;
      replayState.currentTick += deltaSeconds * 64 * replayState.speed;

      const endTick = Number(round.tick_end ?? lastRoundTick(round));
      if (replayState.currentTick >= endTick) {
        replayState.currentTick = endTick;
        replayState.playing = false;
        updatePlayButton();
      } else {
        replayState.animationFrame = requestAnimationFrame(stepReplay);
      }
      drawReplay();
    }

    function interpolatePosition(positions, tick) {
      if (!positions || positions.length === 0) return null;
      if (tick <= positions[0].tick) return positions[0];
      for (let index = 0; index < positions.length - 1; index += 1) {
        const current = positions[index];
        const next = positions[index + 1];
        if (tick >= current.tick && tick <= next.tick) {
          const span = Math.max(1, next.tick - current.tick);
          const ratio = (tick - current.tick) / span;
          return {
            tick,
            x: current.x + (next.x - current.x) * ratio,
            y: current.y + (next.y - current.y) * ratio,
            alive: current.alive && next.alive,
          };
        }
      }
      return positions.at(-1);
    }

    function playerColor(side) {
      return String(side).toLowerCase() === "ct" ? "#5aa9ff" : "#ff9f1c";
    }

    function utilityShortName(type) {
      const value = String(type || "util").toLowerCase();
      if (value.includes("flash")) return "F";
      if (value.includes("smoke")) return "S";
      if (value.includes("molotov") || value.includes("incendiary") || value.includes("inferno")) return "M";
      if (value.includes("he")) return "HE";
      return "U";
    }

    function drawPlayer(ctx, player, position) {
      const selected = String(player.name).toLowerCase() === String(replayState.replay?.selected_player || "").toLowerCase();
      const radius = selected ? 11 : 8;
      ctx.globalAlpha = position.alive ? 1 : 0.45;
      ctx.beginPath();
      ctx.arc(position.x, position.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = playerColor(player.side);
      ctx.fill();
      ctx.lineWidth = selected ? 4 : 2;
      ctx.strokeStyle = selected ? "#ffffff" : "#05070c";
      ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.fillStyle = "#edf3ff";
      ctx.font = selected ? "800 13px system-ui, sans-serif" : "700 11px system-ui, sans-serif";
      ctx.fillText(player.name, position.x + radius + 5, position.y + 4);
      if (!position.alive) {
        ctx.strokeStyle = "#ff4d4d";
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(position.x - 8, position.y - 8);
        ctx.lineTo(position.x + 8, position.y + 8);
        ctx.moveTo(position.x + 8, position.y - 8);
        ctx.lineTo(position.x - 8, position.y + 8);
        ctx.stroke();
      }
    }

    function drawUtility(ctx, event) {
      if (!Number.isFinite(Number(event.x)) || !Number.isFinite(Number(event.y))) return;
      ctx.beginPath();
      ctx.arc(event.x, event.y, 6, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(179, 136, 255, 0.9)";
      ctx.fill();
      ctx.strokeStyle = "#05070c";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = "#ffffff";
      ctx.font = "800 11px system-ui, sans-serif";
      ctx.fillText(utilityShortName(event.grenade_type), event.x + 8, event.y + 4);
    }

    function drawKill(ctx, event) {
      if (!Number.isFinite(Number(event.x)) || !Number.isFinite(Number(event.y))) return;
      ctx.strokeStyle = "#ff4d4d";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(event.x - 9, event.y - 9);
      ctx.lineTo(event.x + 9, event.y + 9);
      ctx.moveTo(event.x + 9, event.y - 9);
      ctx.lineTo(event.x - 9, event.y + 9);
      ctx.stroke();
    }

    function drawReplay() {
      const canvas = document.getElementById("replay-canvas");
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      const round = currentReplayRound();
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#05070c";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      if (!round) {
        drawReplayMessage("Replay data unavailable.");
        return;
      }
      if (replayState.mapImageLoaded) {
        ctx.drawImage(replayState.mapImage, 0, 0, canvas.width, canvas.height);
      } else if (replayState.mapImageError) {
        drawReplayMessage("Map image could not be loaded from static/maps.");
        return;
      } else {
        drawReplayMessage("Loading map image...");
        return;
      }

      const tick = replayState.currentTick;
      for (const event of round.utility.filter((item) => item.tick <= tick)) drawUtility(ctx, event);
      for (const event of round.kills.filter((item) => item.tick <= tick)) drawKill(ctx, event);
      for (const player of round.players) {
        const position = interpolatePosition(player.positions, tick);
        if (position) drawPlayer(ctx, player, position);
      }

      document.getElementById("replay-timeline").value = String(Math.round(tick));
      document.getElementById("replay-tick-label").textContent = `Tick: ${Math.round(tick)}`;
      renderFeeds(round, tick);
    }

    function renderFeeds(round, tick) {
      const killFeed = document.getElementById("kill-feed");
      const utilityFeed = document.getElementById("utility-feed");
      if (!killFeed || !utilityFeed) return;
      const kills = round.kills.filter((item) => item.tick <= tick).slice(-6).reverse();
      const utility = round.utility.filter((item) => item.tick <= tick).slice(-6).reverse();
      killFeed.innerHTML = kills.length
        ? kills.map((event) => `<li>${escapeHtml(event.attacker || "Unknown")} eliminated ${escapeHtml(event.victim || "Unknown")} ${event.weapon ? `with ${escapeHtml(event.weapon)}` : ""}</li>`).join("")
        : "<li>No kills yet.</li>";
      utilityFeed.innerHTML = utility.length
        ? utility.map((event) => `<li>${escapeHtml(event.thrower || "Unknown")} threw ${escapeHtml(event.grenade_type || "utility")}</li>`).join("")
        : "<li>No utility yet.</li>";
    }

    function updateCoachPanel(round) {
      const panel = document.getElementById("coach-summary");
      if (!panel) return;
      if (!round) {
        panel.innerHTML = `
          <div class="coach-block">
            <span class="coach-label">Round summary</span>
            <span class="coach-value">No replay data available.</span>
          </div>
        `;
        return;
      }
      const reportRound = analysisRound(round.round_number);
      const issues = issueList(reportRound?.detected_issues);
      const suggestions = realIssues(reportRound).map(suggestionForIssue);
      panel.innerHTML = `
        <div class="coach-block">
          <span class="coach-label">Round summary</span>
          <span class="coach-value">Round ${escapeHtml(round.round_number)} - ${escapeHtml(reviewResult(reportRound))}</span>
        </div>
        <div class="coach-block">
          <span class="coach-label">Round concern level</span>
          <span class="coach-value ${concernClass(confidence(reportRound))}">${pct(confidence(reportRound))}</span>
        </div>
        <div class="coach-block">
          <span class="coach-label">Why this round was flagged</span>
          <span class="coach-value">${issues.map(escapeHtml).join("<br>")}</span>
        </div>
        <div class="coach-block">
          <span class="coach-label">Suggested improvement</span>
          <span class="coach-value">${(suggestions.length ? suggestions : ["No major coaching issue detected for this round."]).map(escapeHtml).join("<br>")}</span>
        </div>
      `;
    }

    async function loadModelInfo() {
      try {
        const response = await fetch("/model-info");
        const payload = await response.json();
        return response.ok ? payload : { model_status: "model_info_unavailable", load_error: payload.detail || "Request failed" };
      } catch (error) {
        return { model_status: "model_info_unavailable", load_error: String(error) };
      }
    }

    async function loadReplayData(playerName) {
      setReplayStatus("Parsing replay ticks...");
      const replayForm = new FormData(form);
      const response = await fetch(`/replay-data?player_name=${encodeURIComponent(playerName)}`, {
        method: "POST",
        body: replayForm
      });
      const replayPayload = await response.json();
      replayState.replay = replayPayload;
      setRawJson({ analysis: replayState.analysis, model_info: replayState.modelInfo, replay: replayPayload });
      if (!response.ok) {
        setReplayStatus(replayPayload.detail || "Replay extraction failed.");
        drawReplayMessage(replayPayload.detail || "Replay extraction failed.");
        return;
      }
      setupReplay(replayPayload);
    }

    document.addEventListener("keydown", (event) => {
      const tag = event.target?.tagName?.toLowerCase();
      if (["input", "textarea", "select"].includes(tag)) return;
      if (!replayState.replay?.rounds?.length) return;
      if (event.key === "ArrowLeft") {
        event.preventDefault();
        setReplayRound(replayState.roundIndex - 1);
      }
      if (event.key === "ArrowRight") {
        event.preventDefault();
        setReplayRound(replayState.roundIndex + 1);
      }
      if (event.code === "Space") {
        event.preventDefault();
        toggleReplay();
      }
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      button.disabled = true;
      landing.hidden = true;
      report.hidden = true;
      loading.hidden = false;
      replayState.playing = false;
      replayState.replay = null;
      replayState.modelInfo = null;
      replayState.pendingReplayRound = null;
      if (replayState.animationFrame) cancelAnimationFrame(replayState.animationFrame);
      startLoading();

      const playerName = document.getElementById("player_name").value.trim();
      const analysisForm = new FormData(form);
      const selectedFile = document.getElementById("file").files?.[0];

      try {
        console.info("[CS Demo Coach AI] /analyze-demo request start", {
          playerName,
          fileName: selectedFile?.name || null,
          fileSizeBytes: selectedFile?.size || null,
        });
        const response = await fetch(`/analyze-demo?player_name=${encodeURIComponent(playerName)}`, {
          method: "POST",
          body: analysisForm
        });
        const payload = await readResponsePayload(response);
        if (!response.ok) {
          const message = errorMessageFromPayload(payload, `Analysis failed with HTTP ${response.status}.`);
          console.error("[CS Demo Coach AI] /analyze-demo request failure", {
            status: response.status,
            statusText: response.statusText,
            payload,
          });
          showError(message);
          return;
        }
        console.info("[CS Demo Coach AI] /analyze-demo request success", {
          status: response.status,
          roundsAnalyzed: payload.rounds_analyzed,
          player: payload.player,
        });
        setLoadingStage(4);
        const modelInfo = await loadModelInfo();
        stopLoading();
        loading.hidden = true;
        renderReport(payload, modelInfo);
        await loadReplayData(playerName);
      } catch (error) {
        console.error("[CS Demo Coach AI] /analyze-demo request failure", error);
        showError(
          `${String(error)}. If this happened during an AWS upload, the demo may still be parsing or the connection may have been interrupted. Large demos may take 1-3 minutes.`
        );
      } finally {
        button.disabled = false;
      }
    });
  </script>
</body>
</html>
"""
