"""
Türkiye — the reference Market Pack (fully wired: live TCMB data,
listing bridge, localized fear check-in).
"""
from backend.markets.base import ListingSite, MarketPack

TR = MarketPack(
    code="TR",
    name="Türkiye",
    currency="TRY",
    currency_symbol="₺",
    locale="tr-TR",
    languages=["tr", "en"],

    inflation_source="tcmb_evds",      # live CPI (backend/services/evds_service.py)
    housing_index_source="tcmb_evds",  # housing price index for 19 NUTS2 regions
    default_index_ticker="XU100.IS",

    listing_sites=[
        ListingSite("Sahibinden", "https://www.sahibinden.com/arama?query_text={query}"),
        ListingSite("Emlakjet", "https://www.emlakjet.com/arama/?q={query}"),
    ],

    regulator="SPK (Sermaye Piyasası Kurulu)",
    broker_note=(
        "Hisse/fon almak için SPK lisanslı bir aracı kurumda hesap gerekir "
        "(ör. banka aracı kurumları veya dijital aracılar). Hesap açılışı "
        "çoğunlukla uzaktan kimlik doğrulama ile aynı gün tamamlanır."
    ),
    tax_note=(
        "Genel bilgi: BIST hisse alım-satım kazançları için stopaj oranı uzun "
        "süredir %0'dır; mevduat faizi ve fon türlerine göre stopaj değişir; "
        "temettüler stopaja tabidir. Gayrimenkulde tapu harcı ve 5 yıl içinde "
        "satışta değer artış kazancı vergisi gündeme gelir."
    ),
    fear_options={
        "param_eriyor": "Enflasyon param eritiyor",
        "kandirilirim": "Kandırılmaktan korkuyorum",
        "anlamiyorum": "Hiçbir şey anlamıyorum",
        "batiririm": "Batırmaktan korkuyorum",
    },
)
