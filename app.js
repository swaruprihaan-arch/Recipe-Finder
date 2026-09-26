const API_BASE = "https://www.themealdb.com/api/json/v1/1";
const STORAGE_KEY = "recipeFinder.settings.v1";
const FAVORITES_KEY = "recipeFinder.favorites.v1";

const DEFAULT_SETTINGS = {
  theme: "light",
  accent: "#ff6b35",
  view: "grid",
  defaultArea: "",
  defaultCategory: "",
  liveSearch: true,
};

let settings = loadSettings();
let favorites = loadFavorites();
let currentView = settings.view;
let currentMealForModal = null;
let variantMeals = [];
let previousTab = "discover";

const els = {};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  cacheEls();
  applyTheme();
  applyAccent();
  bindTabs();
  bindSettingsUI();
  bindResultControls();
  bindModal();

  await Promise.all([populateCategories(), populateAreas(), populateIngredients(), loadVariantMeals()]);
  applyDefaultFilters();
  setView(currentView, false);
  loadRecipes();
  renderFavoritesTab();
  updateFavCountBadge();

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (settings.theme === "auto") applyTheme();
  });
}

function cacheEls() {
  Object.assign(els, {
    searchInput: document.getElementById("searchInput"),
    searchBtn: document.getElementById("searchBtn"),
    clearBtn: document.getElementById("clearBtn"),
    categoryFilter: document.getElementById("categoryFilter"),
    areaFilter: document.getElementById("areaFilter"),
    ingredientFilter: document.getElementById("ingredientFilter"),
    results: document.getElementById("results"),
    resultCount: document.getElementById("resultCount"),
    loader: document.getElementById("loader"),
    emptyState: document.getElementById("emptyState"),
    detailContent: document.getElementById("detailContent"),
    detailBackBtn: document.getElementById("detailBackBtn"),
    detailFavBtn: document.getElementById("detailFavBtn"),
    viewToggle: document.getElementById("viewToggle"),
    favoritesResults: document.getElementById("favoritesResults"),
    favEmptyState: document.getElementById("favEmptyState"),
    favCount: document.getElementById("favCount"),
    favSummary: document.getElementById("favSummary"),
    clearFavsBtn: document.getElementById("clearFavsBtn"),
    resetSettingsBtn: document.getElementById("resetSettingsBtn"),
    themeSegmented: document.getElementById("themeSegmented"),
    viewSegmented: document.getElementById("viewSegmented"),
    accentSwatches: document.getElementById("accentSwatches"),
    defaultAreaSetting: document.getElementById("defaultAreaSetting"),
    defaultCategorySetting: document.getElementById("defaultCategorySetting"),
    liveSearchToggle: document.getElementById("liveSearchToggle"),
    toast: document.getElementById("toast"),
  });
}

/* ================= Settings persistence ================= */

function loadSettings() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_SETTINGS };
    return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch (e) {
    return { ...DEFAULT_SETTINGS };
  }
}
function saveSettings() { localStorage.setItem(STORAGE_KEY, JSON.stringify(settings)); }

function loadFavorites() {
  try {
    const raw = localStorage.getItem(FAVORITES_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch (e) { return {}; }
}
function saveFavorites() { localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites)); }

/* ================= Theme / Accent ================= */

function applyTheme() {
  let effective = settings.theme;
  if (effective === "auto") {
    effective = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.documentElement.setAttribute("data-theme", effective);
  updateSegmented(els.themeSegmented, settings.theme);
}

function applyAccent() {
  const hex = settings.accent;
  document.documentElement.style.setProperty("--primary", hex);
  document.documentElement.style.setProperty("--primary-dark", shadeColor(hex, -15));
  document.documentElement.style.setProperty("--primary-rgb", hexToRgb(hex));
  document.querySelectorAll("#accentSwatches .swatch").forEach((sw) => {
    sw.classList.toggle("active", sw.dataset.color.toLowerCase() === hex.toLowerCase());
  });
}

function hexToRgb(hex) {
  const m = hex.replace("#", "");
  const r = parseInt(m.substring(0, 2), 16);
  const g = parseInt(m.substring(2, 4), 16);
  const b = parseInt(m.substring(4, 6), 16);
  return `${r},${g},${b}`;
}

function shadeColor(hex, percent) {
  const m = hex.replace("#", "");
  let r = parseInt(m.substring(0, 2), 16);
  let g = parseInt(m.substring(2, 4), 16);
  let b = parseInt(m.substring(4, 6), 16);
  r = Math.max(0, Math.min(255, Math.round(r + (percent / 100) * 255)));
  g = Math.max(0, Math.min(255, Math.round(g + (percent / 100) * 255)));
  b = Math.max(0, Math.min(255, Math.round(b + (percent / 100) * 255)));
  return `#${[r, g, b].map((x) => x.toString(16).padStart(2, "0")).join("")}`;
}

function updateSegmented(container, value) {
  if (!container) return;
  container.querySelectorAll(".seg-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.value === value);
  });
}

/* ================= Tabs ================= */

function bindTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });
}

function switchTab(tab) {
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
  document.querySelectorAll(".tab-panel").forEach((p) => p.classList.toggle("active", p.id === `tab-${tab}`));
  if (tab === "favorites") renderFavoritesTab();
}

/* ================= Settings UI bindings ================= */

function bindSettingsUI() {
  els.themeSegmented.querySelectorAll(".seg-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      settings.theme = btn.dataset.value;
      saveSettings();
      applyTheme();
      showToast(`Theme set to ${btn.dataset.value}`);
    });
  });

  els.viewSegmented.querySelectorAll(".seg-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      settings.view = btn.dataset.value;
      saveSettings();
      updateSegmented(els.viewSegmented, settings.view);
      setView(settings.view);
      showToast(`Default view set to ${btn.dataset.value}`);
    });
  });

  els.accentSwatches.querySelectorAll(".swatch").forEach((sw) => {
    sw.addEventListener("click", () => {
      settings.accent = sw.dataset.color;
      saveSettings();
      applyAccent();
      showToast("Accent color updated");
    });
  });

  els.defaultAreaSetting.addEventListener("change", () => {
    settings.defaultArea = els.defaultAreaSetting.value;
    saveSettings();
    showToast("Default cuisine saved");
  });

  els.defaultCategorySetting.addEventListener("change", () => {
    settings.defaultCategory = els.defaultCategorySetting.value;
    saveSettings();
    showToast("Default category saved");
  });

  els.liveSearchToggle.addEventListener("change", () => {
    settings.liveSearch = els.liveSearchToggle.checked;
    saveSettings();
  });

  els.clearFavsBtn.addEventListener("click", () => {
    if (Object.keys(favorites).length === 0) return;
    favorites = {};
    saveFavorites();
    renderFavoritesTab();
    updateFavCountBadge();
    updateFavSummary();
    refreshCardFavStates();
    showToast("Favorites cleared");
  });

  els.resetSettingsBtn.addEventListener("click", () => {
    settings = { ...DEFAULT_SETTINGS };
    saveSettings();
    applyTheme();
    applyAccent();
    els.defaultAreaSetting.value = "";
    els.defaultCategorySetting.value = "";
    els.liveSearchToggle.checked = true;
    updateSegmented(els.viewSegmented, settings.view);
    setView(settings.view);
    showToast("Settings reset to default");
  });

  updateSegmented(els.themeSegmented, settings.theme);
  updateSegmented(els.viewSegmented, settings.view);
  els.liveSearchToggle.checked = settings.liveSearch;
  updateFavSummary();
}

function applyDefaultFilters() {
  if (settings.defaultArea) {
    els.areaFilter.value = settings.defaultArea;
    els.defaultAreaSetting.value = settings.defaultArea;
  }
  if (settings.defaultCategory) {
    els.categoryFilter.value = settings.defaultCategory;
    els.defaultCategorySetting.value = settings.defaultCategory;
  }
}

function updateFavSummary() {
  const n = Object.keys(favorites).length;
  els.favSummary.textContent = `${n} recipe${n === 1 ? "" : "s"} saved locally`;
}

/* ================= View toggle ================= */

function bindResultControls() {
  els.viewToggle.querySelectorAll(".view-btn").forEach((btn) => {
    btn.addEventListener("click", () => setView(btn.dataset.view));
  });

  els.searchBtn.addEventListener("click", loadRecipes);
  els.searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") loadRecipes();
  });
  let debounceTimer = null;
  els.searchInput.addEventListener("input", () => {
    if (!settings.liveSearch) return;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(loadRecipes, 500);
  });
  els.categoryFilter.addEventListener("change", loadRecipes);
  els.areaFilter.addEventListener("change", loadRecipes);
  els.ingredientFilter.addEventListener("change", loadRecipes);
  els.clearBtn.addEventListener("click", () => {
    els.searchInput.value = "";
    els.categoryFilter.value = "";
    els.areaFilter.value = "";
    els.ingredientFilter.value = "";
    loadRecipes();
  });
}

function setView(view, persist = true) {
  currentView = view;
  els.results.classList.toggle("list-view", view === "list");
  els.favoritesResults.classList.toggle("list-view", view === "list");
  els.viewToggle.querySelectorAll(".view-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });
}

/* ================= Toast ================= */

let toastTimer = null;
function showToast(msg) {
  els.toast.textContent = msg;
  els.toast.classList.add("show");
  els.toast.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { els.toast.classList.remove("show"); }, 2200);
}

/* ================= Data population ================= */

async function populateCategories() {
  try {
    const res = await fetch(`${API_BASE}/list.php?c=list`);
    const data = await res.json();
    fillSelect(els.categoryFilter, data.meals, "strCategory");
    fillSelect(els.defaultCategorySetting, data.meals, "strCategory");

    // Locally-generated categories (Burger, Nuggets) don't exist in
    // TheMealDB's own category list, so add them so those recipes are
    // actually reachable via the filter.
    const extraCategories = ["Burger", "Nuggets"];
    const existingValues = new Set(Array.from(els.categoryFilter.options).map((o) => o.value));
    extraCategories.forEach((cat) => {
      if (!existingValues.has(cat)) {
        fillSelect(els.categoryFilter, [{ strCategory: cat }], "strCategory");
        fillSelect(els.defaultCategorySetting, [{ strCategory: cat }], "strCategory");
      }
    });

    sortSelectOptions(els.categoryFilter);
    sortSelectOptions(els.defaultCategorySetting);
  } catch (e) { console.error("categories failed", e); }
}

async function populateAreas() {
  try {
    const res = await fetch(`${API_BASE}/list.php?a=list`);
    const data = await res.json();
    fillSelect(els.areaFilter, data.meals, "strArea");
    fillSelect(els.defaultAreaSetting, data.meals, "strArea");

    // TheMealDB's own recipe data uses a handful of area names that don't
    // appear in its official area list (e.g. "France" instead of "French",
    // "United States" instead of "American"). Add them so those recipes
    // are actually reachable via the filter.
    const extraAreas = ["Slovakia", "France", "Venezuela", "Argentina", "India", "United States", "Netherlands", "Norway"];
    const existingValues = new Set(Array.from(els.areaFilter.options).map((o) => o.value));
    extraAreas.forEach((area) => {
      if (!existingValues.has(area)) {
        fillSelect(els.areaFilter, [{ strArea: area }], "strArea");
        fillSelect(els.defaultAreaSetting, [{ strArea: area }], "strArea");
      }
    });

    sortSelectOptions(els.areaFilter);
    sortSelectOptions(els.defaultAreaSetting);
  } catch (e) { console.error("areas failed", e); }
}

function sortSelectOptions(select) {
  const placeholder = select.options[0];
  const rest = Array.from(select.options).slice(1);
  rest.sort((a, b) => a.value.localeCompare(b.value));
  select.innerHTML = "";
  select.appendChild(placeholder);
  rest.forEach((opt) => select.appendChild(opt));
}

async function populateIngredients() {
  try {
    const res = await fetch(`${API_BASE}/list.php?i=list`);
    const data = await res.json();
    const sorted = (data.meals || []).sort((a, b) => a.strIngredient.localeCompare(b.strIngredient));
    fillSelect(els.ingredientFilter, sorted, "strIngredient");
  } catch (e) { console.error("ingredients failed", e); }
}

function fillSelect(select, items, key) {
  (items || []).forEach((item) => {
    const opt = document.createElement("option");
    opt.value = item[key];
    opt.textContent = item[key];
    select.appendChild(opt);
  });
}

const LFS_MEDIA_BASE = "https://media.githubusercontent.com/media/swaruprihaan-arch/Recipe-Finder/main";

async function loadVariantMeals() {
  try {
    if (Array.isArray(window.__RECIPE_VARIANT_DATA__)) {
      variantMeals = window.__RECIPE_VARIANT_DATA__;
      return;
    }
    // GitHub Pages does not resolve Git LFS pointers via a same-origin
    // <script>/fetch of variant_meals.json (and the LFS media CDN serves it
    // as text/plain, which browsers refuse to execute as a <script> under
    // nosniff) — so on github.io, fetch the JSON straight from the LFS
    // media CDN and JSON.parse it, which fetch() happily allows.
    const onPages = /\.github\.io$/.test(location.hostname);
    const url = onPages ? `${LFS_MEDIA_BASE}/variant_meals.json` : "variant_meals.json";
    const res = await fetch(url);
    variantMeals = await res.json();
  } catch (e) {
    console.error("failed to load local variant recipes", e);
    variantMeals = [];
  }
}

function searchVariantMeals(query) {
  const q = query.toLowerCase();
  return variantMeals.filter((m) => m.strMeal.toLowerCase().includes(q));
}

function findVariantById(id) {
  return variantMeals.find((m) => m.idMeal === id);
}

/* ================= Recipe loading ================= */

async function loadRecipes() {
  const query = els.searchInput.value.trim();
  const category = els.categoryFilter.value;
  const area = els.areaFilter.value;
  const ingredient = els.ingredientFilter.value;

  setLoading(true);

  try {
    let meals = [];

    if (query) {
      const res = await fetch(`${API_BASE}/search.php?s=${encodeURIComponent(query)}`);
      const data = await res.json();
      const apiMeals = data.meals || [];
      const localMatches = searchVariantMeals(query);
      meals = dedupeMeals([...apiMeals, ...localMatches]);
      meals = applyLocalFilters(meals, category, area, ingredient);
    } else if (category || area || ingredient) {
      const filterSets = [];
      if (category) filterSets.push(await fetchFilterList("c", category));
      if (area) filterSets.push(await fetchFilterList("a", area));
      if (ingredient) filterSets.push(await fetchFilterList("i", ingredient));
      let apiMeals = intersectById(filterSets);
      const localMeals = applyLocalFilters(variantMeals, category, area, ingredient);
      meals = dedupeMeals([...apiMeals, ...localMeals]);
    } else {
      const allReal = await getAllMealsCached();
      meals = dedupeMeals([...allReal, ...variantMeals]);
    }

    renderResults(meals);
  } catch (e) {
    console.error("load failed", e);
    renderResults([]);
  } finally {
    setLoading(false);
  }
}

function dedupeMeals(meals) {
  const seen = new Set();
  return meals.filter((m) => {
    if (seen.has(m.idMeal)) return false;
    seen.add(m.idMeal);
    return true;
  });
}

async function fetchFilterList(param, value) {
  const res = await fetch(`${API_BASE}/filter.php?${param}=${encodeURIComponent(value)}`);
  const data = await res.json();
  return data.meals || [];
}

const ALL_MEALS_CACHE_KEY = "recipeFinder.allMeals.v1";
const ALL_MEALS_TTL_MS = 24 * 60 * 60 * 1000;
let allMealsMemoryCache = null;

async function getAllMealsCached() {
  if (allMealsMemoryCache) return allMealsMemoryCache;

  try {
    const raw = localStorage.getItem(ALL_MEALS_CACHE_KEY);
    if (raw) {
      const cached = JSON.parse(raw);
      if (cached.ts && Date.now() - cached.ts < ALL_MEALS_TTL_MS && Array.isArray(cached.meals) && cached.meals.length > 0) {
        allMealsMemoryCache = cached.meals;
        return allMealsMemoryCache;
      }
    }
  } catch (e) { /* ignore corrupt cache */ }

  const letters = "abcdefghijklmnopqrstuvwxyz".split("");
  const results = await Promise.all(
    letters.map((l) =>
      fetch(`${API_BASE}/search.php?f=${l}`)
        .then((r) => r.json())
        .then((d) => d.meals || [])
        .catch(() => [])
    )
  );

  const seen = new Set();
  const meals = [];
  results.flat().forEach((m) => {
    if (!seen.has(m.idMeal)) {
      seen.add(m.idMeal);
      meals.push(m);
    }
  });

  allMealsMemoryCache = meals;
  try {
    localStorage.setItem(ALL_MEALS_CACHE_KEY, JSON.stringify({ ts: Date.now(), meals }));
  } catch (e) { /* storage full or unavailable, ignore */ }

  return meals;
}

function intersectById(lists) {
  if (lists.length === 0) return [];
  if (lists.length === 1) return lists[0];
  const idSets = lists.map((list) => new Set(list.map((m) => m.idMeal)));
  const common = lists[0].filter((m) => idSets.every((set) => set.has(m.idMeal)));
  const seen = new Set();
  return common.filter((m) => {
    if (seen.has(m.idMeal)) return false;
    seen.add(m.idMeal);
    return true;
  });
}

function applyLocalFilters(meals, category, area, ingredient) {
  return meals.filter((m) => {
    if (category && m.strCategory !== category) return false;
    if (area && m.strArea !== area) return false;
    if (ingredient) {
      const ingredients = getIngredients(m).map((i) => i.name.toLowerCase());
      if (!ingredients.includes(ingredient.toLowerCase())) return false;
    }
    return true;
  });
}

function setLoading(isLoading) {
  if (isLoading) {
    els.loader.innerHTML = Array.from({ length: 8 }).map(() => `<div class="skeleton-card"></div>`).join("");
    els.loader.classList.remove("hidden");
    els.results.innerHTML = "";
    els.emptyState.classList.add("hidden");
    els.resultCount.textContent = "";
  } else {
    els.loader.classList.add("hidden");
  }
}

/* ================= Rendering ================= */

const PAGE_SIZE = 60;
let currentMeals = [];
let currentPage = 0;

function renderResults(meals) {
  currentMeals = meals || [];
  currentPage = 0;
  els.results.innerHTML = "";

  if (!currentMeals.length) {
    els.emptyState.classList.remove("hidden");
    els.resultCount.textContent = "";
    removeLoadMoreBtn();
    return;
  }

  els.emptyState.classList.add("hidden");
  els.resultCount.textContent = `${currentMeals.length} recipe${currentMeals.length === 1 ? "" : "s"} found`;
  renderNextPage();
}

function renderNextPage() {
  const start = currentPage * PAGE_SIZE;
  const pageItems = currentMeals.slice(start, start + PAGE_SIZE);
  const frag = document.createDocumentFragment();
  pageItems.forEach((meal) => frag.appendChild(buildCard(meal)));
  els.results.appendChild(frag);
  currentPage += 1;
  updateLoadMoreBtn();
}

function updateLoadMoreBtn() {
  removeLoadMoreBtn();
  const shown = currentPage * PAGE_SIZE;
  if (shown < currentMeals.length) {
    const btn = document.createElement("button");
    btn.id = "loadMoreBtn";
    btn.className = "load-more-btn";
    btn.textContent = `Load more (${currentMeals.length - shown} remaining)`;
    btn.addEventListener("click", renderNextPage);
    els.results.insertAdjacentElement("afterend", btn);
  }
}

function removeLoadMoreBtn() {
  const existing = document.getElementById("loadMoreBtn");
  if (existing) existing.remove();
}

function unicodeSafeBtoa(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

const FALLBACK_THUMB = "data:image/svg+xml;base64," + unicodeSafeBtoa(
  '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400">' +
  '<rect width="400" height="400" fill="#e0d5c4"/>' +
  '<text x="200" y="200" font-size="120" text-anchor="middle" dominant-baseline="middle">🍽️</text>' +
  '</svg>'
);

// Guarantees every meal object has a usable image + YouTube + source link,
// even if TheMealDB itself didn't provide one for that particular real recipe.
function ensureMealHasLinksAndImage(meal) {
  if (!meal.strMealThumb) {
    meal.strMealThumb = FALLBACK_THUMB;
  }
  const name = meal.strMeal || "recipe";
  if (!meal.strYoutube) {
    meal.strYoutube = `https://www.youtube.com/results?search_query=${encodeURIComponent(name + " recipe")}`;
    meal.strYoutubeIsSearch = true;
  }
  if (!meal.strSource) {
    meal.strSource = `https://www.google.com/search?q=${encodeURIComponent(name + " recipe")}`;
    meal.strSourceIsSearch = true;
  }
}

// Best-effort mapping from TheMealDB-style area/nationality names to the
// actual Wikipedia article slug for that cuisine (falls back to a Wikipedia
// search link when there's no dedicated "X cuisine" article).
const CUISINE_WIKI_OVERRIDES = {
  "United States": "American_cuisine",
  "Antiguan, Barbudan": "Antigua_and_Barbuda", "Bosnian, Herzegovinian": "Bosnia_and_Herzegovina_cuisine",
  "France": "French_cuisine", "Netherlands": "Dutch_cuisine", "Norway": "Norwegian_cuisine",
  "Venezuela": "Venezuelan_cuisine", "Argentina": "Argentine_cuisine", "India": "Indian_cuisine",
  "Slovakia": "Slovak_cuisine", "British": "British_cuisine", "Hong Konger": "Cuisine_of_Hong_Kong",
  "Gibraltar": "Gibraltarian_cuisine", "Djibouti": "Djiboutian_cuisine",
};

function cuisineLink(area) {
  if (!area) return "";
  if (CUISINE_WIKI_OVERRIDES[area]) {
    return `https://en.wikipedia.org/wiki/${CUISINE_WIKI_OVERRIDES[area]}`;
  }
  return `https://en.wikipedia.org/wiki/${encodeURIComponent(area.replace(/ /g, "_"))}_cuisine`;
}

function buildCard(meal) {
  ensureMealHasLinksAndImage(meal);
  const card = document.createElement("div");
  card.className = "recipe-card";
  card.dataset.id = meal.idMeal;
  const isFav = !!favorites[meal.idMeal];
  const isVariant = !!meal.isVariant;
  card.innerHTML = `
    <img src="${meal.strMealThumb}" alt="${meal.strMeal}" loading="lazy" onerror="this.onerror=null;this.src='${FALLBACK_THUMB}';">
    ${isVariant ? `<span class="variant-badge">✨ ${meal.variantLabel || "Variant"}</span>` : ""}
    <button class="card-fav-btn ${isFav ? "active" : ""}" data-fav-toggle title="Save to favorites">${isFav ? "♥" : "♡"}</button>
    <div class="recipe-card-body">
      <div class="recipe-card-title">${meal.strMeal}</div>
      <div class="recipe-tags">
        ${meal.strCategory ? `<span class="tag">${meal.strCategory}</span>` : ""}
        ${meal.strArea ? `<a href="${cuisineLink(meal.strArea)}" target="_blank" rel="noopener" class="tag area" data-cuisine-link title="Learn about ${meal.strArea} cuisine">${meal.strArea}</a>` : ""}
      </div>
    </div>
  `;
  card.addEventListener("click", (e) => {
    if (e.target.closest("[data-fav-toggle]") || e.target.closest("[data-cuisine-link]")) return;
    openRecipe(meal.idMeal);
  });
  card.querySelector("[data-fav-toggle]").addEventListener("click", (e) => {
    e.stopPropagation();
    toggleFavorite(meal);
  });
  const cuisineEl = card.querySelector("[data-cuisine-link]");
  if (cuisineEl) cuisineEl.addEventListener("click", (e) => e.stopPropagation());
  return card;
}

function refreshCardFavStates() {
  document.querySelectorAll(".recipe-card").forEach((card) => {
    const id = card.dataset.id;
    const btn = card.querySelector("[data-fav-toggle]");
    if (!btn) return;
    const isFav = !!favorites[id];
    btn.classList.toggle("active", isFav);
    btn.textContent = isFav ? "♥" : "♡";
  });
}

/* ================= Favorites ================= */

function toggleFavorite(meal) {
  const id = meal.idMeal;
  if (favorites[id]) {
    delete favorites[id];
    showToast("Removed from favorites");
  } else {
    favorites[id] = {
      idMeal: meal.idMeal,
      strMeal: meal.strMeal,
      strMealThumb: meal.strMealThumb,
      strCategory: meal.strCategory,
      strArea: meal.strArea,
    };
    showToast("Added to favorites");
  }
  saveFavorites();
  refreshCardFavStates();
  updateFavCountBadge();
  updateFavSummary();
  if (document.getElementById("tab-favorites").classList.contains("active")) {
    renderFavoritesTab();
  }
  if (currentMealForModal && currentMealForModal.idMeal === id) {
    updateModalFavButton(id);
  }
}

function updateFavCountBadge() {
  const n = Object.keys(favorites).length;
  els.favCount.textContent = n;
  els.favCount.classList.toggle("hidden", n === 0);
}

function renderFavoritesTab() {
  const list = Object.values(favorites);
  els.favoritesResults.innerHTML = "";
  if (list.length === 0) {
    els.favEmptyState.classList.remove("hidden");
    return;
  }
  els.favEmptyState.classList.add("hidden");
  const frag = document.createDocumentFragment();
  list.forEach((meal) => frag.appendChild(buildCard(meal)));
  els.favoritesResults.appendChild(frag);
}

/* ================= Full-screen recipe detail ================= */

function bindModal() {
  els.detailBackBtn.addEventListener("click", closeDetail);
  els.detailFavBtn.addEventListener("click", () => {
    if (currentMealForModal) toggleFavorite(currentMealForModal);
  });
}

async function openRecipe(id) {
  const activePanel = document.querySelector(".tab-panel.active");
  previousTab = activePanel ? activePanel.id.replace("tab-", "") : "discover";

  els.detailContent.innerHTML = `<div class="skeleton-grid" style="padding:32px;"><div class="skeleton-card" style="height:440px;grid-column:1/-1;"></div></div>`;
  switchTab("detail");
  window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });

  try {
    let meal = null;
    const localVariant = findVariantById(id);

    if (localVariant) {
      meal = localVariant;
    } else {
      const res = await fetch(`${API_BASE}/lookup.php?i=${id}`);
      const data = await res.json();
      meal = data.meals && data.meals[0];
    }

    if (!meal) return;

    currentMealForModal = meal;
    ensureMealHasLinksAndImage(meal);
    const ingredients = getIngredients(meal);
    const isVariant = !!meal.isVariant;
    const isSynthetic = !!meal.isSynthetic;
    const noticeText = `✨ This is a generated ${meal.variantLabel} variant based on a real recipe — not sourced from TheMealDB.`;

    els.detailContent.innerHTML = `
      <div class="detail-hero-wrap">
        <img class="detail-hero" src="${meal.strMealThumb}" alt="${meal.strMeal}" onerror="this.onerror=null;this.src='${FALLBACK_THUMB}';">
      </div>
      <div class="detail-body">
        ${isVariant && !isSynthetic ? `<div class="variant-notice">${noticeText}</div>` : ""}
        <h1>${meal.strMeal}</h1>
        <div class="detail-meta">
          ${meal.strCategory ? `<span class="tag">${meal.strCategory}</span>` : ""}
          ${meal.strArea ? `<a href="${cuisineLink(meal.strArea)}" target="_blank" rel="noopener" class="tag area">${meal.strArea}</a>` : ""}
          ${meal.strTags ? meal.strTags.split(",").map((t) => `<span class="tag">${t.trim()}</span>`).join("") : ""}
        </div>

        <div class="detail-grid">
          <div>
            <h3>Ingredients</h3>
            <ul class="ingredient-list">
              ${ingredients.map((i) => `<li><span>${i.name}</span><span class="measure">${i.measure}</span></li>`).join("")}
            </ul>
          </div>
          <div>
            <h3>Instructions</h3>
            <div class="instructions">${meal.strInstructions || "No instructions provided."}</div>
            <div class="detail-links">
              ${meal.strYoutube ? `<a href="${meal.strYoutube}" target="_blank">▶ Watch on YouTube</a>` : ""}
              ${meal.strSource ? `<a href="${meal.strSource}" target="_blank">🔗 Original Source</a>` : ""}
            </div>
          </div>
        </div>
      </div>
    `;
    updateModalFavButton(id);
  } catch (e) {
    console.error("recipe fetch failed", e);
    els.detailContent.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div>Failed to load recipe.</div>`;
  }
}

function updateModalFavButton(id) {
  const isFav = !!favorites[id];
  els.detailFavBtn.classList.toggle("active", isFav);
  els.detailFavBtn.textContent = isFav ? "♥ Saved" : "♡ Save";
}

function closeDetail() {
  currentMealForModal = null;
  switchTab(previousTab);
}

/* ================= Helpers ================= */

function getIngredients(meal) {
  const list = [];
  for (let i = 1; i <= 20; i++) {
    const name = meal[`strIngredient${i}`];
    const measure = meal[`strMeasure${i}`];
    if (name && name.trim()) {
      list.push({ name: name.trim(), measure: (measure || "").trim() });
    }
  }
  return list;
}
