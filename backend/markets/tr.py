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
    # Deliberately no specific holding periods or rates: tax rules change, and a
    # stale number here would read as a promise. Point at the boundary instead.
    tax_note=(
        "Vergilendirme, varlık türüne ve edinim tarihine göre değişir; kurallar "
        "zaman içinde güncellenir. Gayrimenkulde tapu harcı alım anında doğar, "
        "satış hâlinde ise değer artış kazancı vergisi gündeme gelebilir. "
        "Hesaplamalarımız evde oturmaya/varlığı elde tutmaya devam ettiğin "
        "varsayımına dayanır ve satış vergilerini içermez. Kendi durumun için "
        "güncel mevzuata veya bir mali müşavire başvur."
    ),
    fear_options={
        "param_eriyor": "Enflasyon param eritiyor",
        "kandirilirim": "Kandırılmaktan korkuyorum",
        "anlamiyorum": "Hiçbir şey anlamıyorum",
        "batiririm": "Batırmaktan korkuyorum",
    },
)
