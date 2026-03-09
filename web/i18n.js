// i18n.js - Localization Engine
const I18N_CACHE = {};
const DEFAULT_LANG = "en";

async function loadLocale(lang) {
    if (I18N_CACHE[lang]) return I18N_CACHE[lang];

    try {
        const response = await fetch(`locales/${lang}.json`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        I18N_CACHE[lang] = data;
        return data;
    } catch (error) {
        console.error(`Error loading locale ${lang}:`, error);
        // Fallback to English if translation fails
        if (lang !== DEFAULT_LANG) {
            return await loadLocale(DEFAULT_LANG);
        }
        return {};
    }
}

function applyTranslations(translations, pageContext = "wizard") {
    if (!translations || !translations[pageContext]) return;

    const contextData = translations[pageContext];

    document.querySelectorAll("[data-i18n]").forEach(element => {
        const key = element.getAttribute("data-i18n");
        if (contextData[key]) {
            // Check if it's an input with a placeholder
            if (element.tagName === "INPUT" && element.hasAttribute("placeholder")) {
                element.placeholder = contextData[key];
            } else {
                element.innerHTML = contextData[key];
            }
        }
    });

    // Handle select options with data-i18n attributes
    document.querySelectorAll("option[data-i18n]").forEach(element => {
        const key = element.getAttribute("data-i18n");
        if (contextData[key]) {
            // For options we ensure just textContent to avoid breaking select structure
            element.textContent = contextData[key];
        }
    });
}

async function setLanguage(lang, pageContext = "wizard") {
    const validLangs = ["en", "ua", "de"];
    const actualLang = validLangs.includes(lang) ? lang : DEFAULT_LANG;

    localStorage.setItem("crw_lang", actualLang);
    const translations = await loadLocale(actualLang);

    applyTranslations(translations, pageContext);

    // Dispatch event so other modules know translation is complete
    document.dispatchEvent(new CustomEvent('i18nUpdated', { detail: { lang: actualLang } }));
}

function getCurrentLanguage() {
    return localStorage.getItem("crw_lang") || DEFAULT_LANG;
}

// Export functions for module usage (if using type="module")
// Fallback to window for ease of use in existing non-module setup
window.crw_i18n = {
    setLanguage,
    getCurrentLanguage,
    loadLocale
};
