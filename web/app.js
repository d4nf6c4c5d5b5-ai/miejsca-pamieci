/* Miejsca Pamięci — aplikacja mapy (bez frameworków, bez kroku budowania). */
(() => {
  "use strict";

  const PAGE = 80;
  const t0 = performance.now();
  const $ = (sel) => document.querySelector(sel);
  const fmt = new Intl.NumberFormat("pl-PL");
  const fold = (s) => (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");

  const state = { q: "", woj: "", off: new Set(), near: null, shown: PAGE, openId: null };
  let DATA, ITEMS = [], CATS = [], map, cluster, filtered = [], youMarker;

  /* ---------- URL (stan do udostępnienia linkiem) ---------- */
  function readHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    state.q = p.get("q") || "";
    state.woj = p.get("woj") || "";
    state.off = new Set((p.get("bez") || "").split(",").filter(Boolean));
    state.openId = p.get("obiekt");
  }
  function writeHash() {
    const p = new URLSearchParams();
    if (state.q) p.set("q", state.q);
    if (state.woj) p.set("woj", state.woj);
    if (state.off.size) p.set("bez", [...state.off].join(","));
    if (state.openId) p.set("obiekt", state.openId);
    const h = p.toString();
    history.replaceState(null, "", h ? `#${h}` : location.pathname + location.search);
  }

  /* ---------- Dane ---------- */
  async function load() {
    const res = await fetch("data/places.json", { credentials: "omit" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    DATA = await res.json();
    const tFetch = performance.now();
    CATS = DATA.categories.map((c, bit) => ({ ...c, bit: 1 << bit }));
    const col = Object.fromEntries(DATA.columns.map((c, i) => [c, i]));
    ITEMS = DATA.rows.map((r, i) => {
      const m = r[col.mask];
      const primary = CATS.find((c) => m & c.bit) || CATS[CATS.length - 1];
      return {
        i, id: r[col.id], name: r[col.name], func: r[col.func], chron: r[col.chron], mask: m,
        lat: r[col.lat], lon: r[col.lon], woj: DATA.voivodeships[r[col.woj]], powiat: r[col.powiat],
        gmina: r[col.gmina], place: r[col.place], addr: r[col.addr], prec: r[col.prec], src: r[col.src],
        primary,
        key: fold(`${r[col.name]} ${r[col.place]} ${r[col.gmina]} ${r[col.powiat]} ${r[col.func]}`),
      };
    });
    return tFetch;
  }

  /* ---------- Mapa ---------- */
  function initMap() {
    map = L.map("map", { preferCanvas: true, zoomControl: true, minZoom: 5, maxBounds: [[47, 9], [57, 28]] })
      .setView([52.0, 19.2], 6);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | dane: NID, GUGiK (dane.gov.pl)',
    }).addTo(map);
    cluster = L.markerClusterGroup({
      chunkedLoading: true, chunkInterval: 120, showCoverageOnHover: false,
      maxClusterRadius: (z) => (z < 9 ? 55 : 35), spiderfyDistanceMultiplier: 1.4,
    });
    map.addLayer(cluster);
    const renderer = L.canvas({ padding: 0.3 });
    for (const it of ITEMS) {
      it.marker = L.circleMarker([it.lat, it.lon], {
        renderer, radius: it.src === 1 ? 9 : 7, weight: 2, color: "#fff",
        fillColor: it.primary.color, fillOpacity: 0.95,
      });
      it.marker.bindPopup(() => card(it), { maxWidth: 360, autoPanPadding: [24, 24] });
      it.marker.on("popupopen", () => { state.openId = it.id; writeHash(); });
      it.marker.on("popupclose", () => { if (state.openId === it.id) { state.openId = null; writeHash(); } });
    }
  }

  /* ---------- Karta obiektu ---------- */
  const PREC = [
    "Dokładne położenie obiektu.",
    "Rejestr zabytków nie podaje współrzędnych: punkt wskazuje miejscowość, w której leży obiekt.",
    "Punkt wskazuje siedzibę gminy, w której leży obiekt.",
  ];
  function card(it) {
    const node = $("#card").content.firstElementChild.cloneNode(true);
    const cats = node.querySelector(".plaque-cats");
    for (const c of CATS) {
      if (!(it.mask & c.bit)) continue;
      const s = document.createElement("span");
      s.textContent = c.label;
      s.style.setProperty("--c", c.color);
      cats.append(s);
    }
    node.querySelector(".plaque-name").textContent = cap(it.name);
    node.querySelector(".plaque-chron").textContent = it.src === 1 ? `Pomnik Historii od ${it.chron}` : it.chron;
    node.querySelector(".plaque-func").textContent = it.func || "—";
    node.querySelector(".plaque-addr").textContent =
      [it.place + (it.addr ? `, ${it.addr}` : ""), `gm. ${it.gmina.replace(/\s*\(gm\..*\)/, "")}`, it.woj].join(", ");
    node.querySelector(".plaque-note").textContent = PREC[it.prec];
    const rej = it.src === 1 ? "pomniki-historii" : "rejestr-zabytkow";
    node.querySelector(".plaque-nid").href =
      `https://zabytek.pl/pl/obiekty/zabytek?inspire_id=${encodeURIComponent(it.id)}&rejestr=${rej}`;
    return node;
  }
  const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);

  /* ---------- Filtry ---------- */
  function baseMatch() {
    const tokens = fold(state.q).split(/\s+/).filter(Boolean);
    return ITEMS.filter((it) =>
      (!state.woj || it.woj === state.woj) && tokens.every((t) => it.key.includes(t)));
  }

  function apply({ fit = false } = {}) {
    const t = performance.now();
    const base = baseMatch();
    const offMask = CATS.filter((c) => state.off.has(c.key)).reduce((a, c) => a | c.bit, 0);
    const allMask = CATS.reduce((a, c) => a | c.bit, 0);
    const onMask = allMask & ~offMask;
    filtered = base.filter((it) => it.mask & onMask);

    // liczniki przy kategoriach (dla bieżącego wyszukiwania i województwa)
    for (const c of CATS) c.count = 0;
    for (const it of base) for (const c of CATS) if (it.mask & c.bit) c.count++;
    for (const c of CATS) c.countEl.textContent = fmt.format(c.count);

    if (state.near) {
      for (const it of filtered) it.dist = haversine(state.near, it);
      filtered.sort((a, b) => a.dist - b.dist);
    } else {
      filtered.sort((a, b) => b.primary === a.primary ? a.name.localeCompare(b.name, "pl")
        : CATS.indexOf(a.primary) - CATS.indexOf(b.primary));
    }

    cluster.clearLayers();
    cluster.addLayers(filtered.map((it) => it.marker));
    state.shown = PAGE;
    renderList();
    if (fit && filtered.length && (state.q || state.woj)) {
      map.fitBounds(L.latLngBounds(filtered.map((it) => [it.lat, it.lon])).pad(0.15), { maxZoom: 12 });
    }
    writeHash();
    $("#perf").dataset.filterMs = (performance.now() - t).toFixed(0);
  }

  function renderList() {
    const ol = $("#results");
    const n = filtered.length;
    $("#count").textContent = n === 0 ? "Brak miejsc dla tych filtrów"
      : state.near ? `Najbliżej Ciebie: ${fmt.format(n)} ${plural(n)}`
      : `${fmt.format(n)} ${plural(n)} na mapie`;
    const frag = document.createDocumentFragment();
    for (const it of filtered.slice(0, state.shown)) {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.type = "button";
      b.style.setProperty("--c", it.primary.color);
      const bar = document.createElement("span"); bar.className = "bar";
      const tt = document.createElement("span"); tt.className = "t"; tt.textContent = cap(it.name);
      const s = document.createElement("span"); s.className = "s";
      s.textContent = [it.place, it.chron, it.dist != null && state.near ? km(it.dist) : ""].filter(Boolean).join(", ");
      b.append(bar, tt, s);
      b.addEventListener("click", () => focusItem(it));
      li.append(b);
      frag.append(li);
    }
    ol.replaceChildren(frag);
    if (n === 0) {
      const li = document.createElement("li");
      li.className = "empty";
      li.textContent = state.q ? "Sprawdź pisownię albo wyczyść wyszukiwanie i włącz więcej kategorii." : "Włącz przynajmniej jedną kategorię.";
      ol.append(li);
    }
    $("#more").hidden = n <= state.shown;
  }

  function focusItem(it) {
    cluster.zoomToShowLayer(it.marker, () => it.marker.openPopup());
    if (matchMedia("(max-width: 760px)").matches) setSheet(false);
  }

  function setSheet(open) {
    const p = $("#panel");
    p.classList.toggle("collapsed", !open);
    if (!open) p.scrollTop = 0;
    $("#sheetToggle").setAttribute("aria-expanded", String(open));
  }

  const plural = (n) => (n === 1 ? "miejsce" : [2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100) ? "miejsca" : "miejsc");
  const km = (d) => (d < 1 ? `${Math.round(d * 1000)} m` : `${d.toFixed(d < 10 ? 1 : 0).replace(".", ",")} km`);
  function haversine(a, b) {
    const R = 6371, r = Math.PI / 180;
    const dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(x));
  }

  /* ---------- Interfejs ---------- */
  function initUI() {
    const ul = $("#cats");
    for (const c of CATS) {
      const li = document.createElement("li");
      li.innerHTML = `<label title=""><input type="checkbox"><span class="dot"></span><span class="name"></span><span class="n"></span></label>`;
      const input = li.querySelector("input");
      li.querySelector("label").title = c.description;
      li.querySelector("label").style.setProperty("--c", c.color);
      li.querySelector(".name").textContent = c.label;
      c.countEl = li.querySelector(".n");
      input.checked = !state.off.has(c.key);
      input.addEventListener("change", () => {
        input.checked ? state.off.delete(c.key) : state.off.add(c.key);
        apply();
      });
      ul.append(li);
    }

    const sel = $("#woj");
    for (const w of [...DATA.voivodeships].sort((a, b) => a.localeCompare(b, "pl"))) sel.add(new Option(w, w));
    sel.value = state.woj;
    sel.addEventListener("change", () => { state.woj = sel.value; apply({ fit: true }); });

    const q = $("#q");
    q.value = state.q;
    let timer;
    q.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => { state.q = q.value.trim(); state.near = null; apply({ fit: true }); }, 160);
    });

    $("#more").addEventListener("click", () => { state.shown += PAGE; renderList(); });
    $("#sheetToggle").addEventListener("click", () => setSheet($("#panel").classList.contains("collapsed")));

    $("#near").addEventListener("click", () => {
      const btn = $("#near");
      if (!navigator.geolocation) { $("#count").textContent = "Ta przeglądarka nie udostępnia lokalizacji."; return; }
      btn.setAttribute("aria-busy", "true");
      navigator.geolocation.getCurrentPosition((pos) => {
        btn.removeAttribute("aria-busy");
        state.near = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        state.q = ""; q.value = ""; state.woj = ""; sel.value = "";
        if (youMarker) youMarker.remove();
        youMarker = L.marker([state.near.lat, state.near.lon], {
          icon: L.divIcon({ className: "", html: '<div class="you" title="Twoja lokalizacja"></div>', iconSize: [16, 16] }),
        }).addTo(map);
        map.setView([state.near.lat, state.near.lon], 11);
        apply();
      }, () => {
        btn.removeAttribute("aria-busy");
        $("#count").textContent = "Nie udało się ustalić lokalizacji. Zezwól na dostęp do lokalizacji albo wpisz miejscowość.";
      }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 });
    });
  }

  /* ---------- Biblioteki mapy: lokalne, a w razie braku — CDN jako zapas ---------- */
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error(`Nie wczytano ${src}`));
      document.head.append(s);
    });
  }
  function loadCss(href) {
    const l = document.createElement("link");
    l.rel = "stylesheet";
    l.href = href;
    document.head.append(l);
  }
  async function ensureLeaflet() {
    if (window.L && L.markerClusterGroup) return;
    const cdn = "https://cdn.jsdelivr.net/npm/";
    if (!window.L) {
      loadCss(`${cdn}leaflet@1.9.4/dist/leaflet.css`);
      await loadScript(`${cdn}leaflet@1.9.4/dist/leaflet.js`);
    }
    loadCss(`${cdn}leaflet.markercluster@1.5.3/dist/MarkerCluster.css`);
    await loadScript(`${cdn}leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js`);
  }

  /* ---------- Start ---------- */
  readHash();
  window.addEventListener("DOMContentLoaded", async () => {
    try {
      const [tFetch] = await Promise.all([load(), ensureLeaflet()]);
      initMap();
      initUI();
      apply({ fit: true });
      // performance.now() liczy od początku nawigacji, więc to pełny czas od wejścia na stronę.
      const total = performance.now();
      const sec = (ms) => (ms / 1000).toFixed(2).replace(".", ",");
      const gen = new Date(DATA.generated).toLocaleDateString("pl-PL");
      $("#perf").textContent =
        `Mapa gotowa w ${sec(total)} s od otwarcia strony (${fmt.format(ITEMS.length)} ${plural(ITEMS.length)}, ` +
        `dane przetworzone w ${sec(tFetch - t0)} s). Aktualizacja danych: ${gen}.`;
      if (state.openId) {
        const it = ITEMS.find((x) => x.id === state.openId);
        if (it) focusItem(it);
      }
    } catch (err) {
      $("#count").textContent = window.L
        ? "Nie udało się wczytać danych. Odśwież stronę; jeśli uruchamiasz lokalnie, najpierw zbuduj dane: python3 scripts/fetch_data.py"
        : "Nie udało się wczytać mapy. Sprawdź połączenie z internetem i odśwież stronę.";
      console.error(err);
    }
  });
})();
