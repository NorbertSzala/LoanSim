"""Small presentation catalog; widgets use keys so English can be added later."""

import re

PL = {
    "app_name": "LoanSim",
    "empty": "—",
    "tab_simulation": "Symulacja",
    "tab_results": "Wyniki",
    "tab_history": "Historia",
    "scenario": "Scenariusz",
    "default_scenario_name": "Nowa symulacja",
    "name": "Nazwa",
    "color": "Kolor (#RRGGBB)",
    "notes": "Notatki",
    "property": "Nieruchomość",
    "price": "Cena (PLN)",
    "down_payment": "Wkład własny (PLN)",
    "purchase_loan": "Kwota kredytu (PLN)",
    "down_fraction": "Udział wkładu (0–1)",
    "ltv": "LTV (0–1)",
    "loan": "Kredyt",
    "term_months": "Okres (miesiące)",
    "start_date": "Data rozpoczęcia (RRRR-MM-DD)",
    "installment": "Rodzaj rat",
    "rate": "Oprocentowanie",
    "rate_type": "Model stopy",
    "nominal_annual": "Stopa nominalna roczna (np. 0.07)",
    "index_annual": "Indeks początkowy",
    "margin": "Marża",
    "index_name": "Nazwa indeksu",
    "fixed_months": "Okres stały (miesiące)",
    "follow_on_nominal": "Stopa po okresie stałym (scenariusz)",
    "as_of_date": "Stan wiedzy na dzień",
    "overpayments": "Nadpłaty",
    "regular_extra": "Stała nadpłata (PLN)",
    "monthly_cap": "Limit miesięczny (PLN)",
    "response": "Efekt nadpłaty",
    "charges": "Koszty dodatkowe",
    "calculate": "Oblicz",
    "add": "Dodaj",
    "remove": "Usuń zaznaczony",
    "lock": "Zablokuj",
    "origin_missing": "Brak",
    "origin_entered": "Wprowadzone",
    "origin_derived": "Wyliczone",
    "locked_tooltip": "Wartość wprowadzona i zablokowana",
    "entered_annuity": "Rata równa wprowadzona (PLN)",
    "estimated_annuity": "Szacowana rata równa (PLN)",
    "installment_annuity": "Raty równe",
    "installment_declining": "Raty malejące",
    "rate_fixed": "Stała",
    "rate_variable": "Zmienna",
    "rate_periodic_fixed": "Okresowo stała → stała",
    "rate_periodic_variable": "Okresowo stała → zmienna",
    "manual_index": "Indeks ręczny",
    "rate_path": "Dalsza ścieżka indeksu",
    "rate_path_headers": "Okres|Indeks|Rodzaj|Źródło|Obserwacja|Publikacja",
    "add_rate": "Dodaj obserwację",
    "remove_rate": "Usuń obserwację",
    "response_shorten": "Skróć okres",
    "response_lower": "Obniż ratę",
    "one_time": "Nadpłaty jednorazowe",
    "one_time_headers": "Okres|Kwota (PLN)",
    "add_extra": "Dodaj nadpłatę",
    "remove_extra": "Usuń nadpłatę",
    "charge_headers": "Nazwa|Kwota|Kategoria|Częstość|Źródło środków|Odbiorca|Od|Do",
    "add_charge": "Dodaj koszt",
    "remove_charge": "Usuń koszt",
    "validation_error": "Błąd walidacji",
    "observation_hypothetical": "Hipotetyczna",
    "observation_historical": "Historyczna",
    "charge_mandatory": "Obowiązkowy kredytowy",
    "charge_optional": "Opcjonalny kredytowy",
    "charge_acquisition": "Zakup",
    "cadence_once": "Jednorazowy",
    "cadence_monthly": "Co miesiąc",
    "funding_own": "Środki własne",
    "funding_financed": "Finansowany",
    "payee_lender": "Kredytodawca",
    "payee_other": "Inny",
    "default_charge_name": "Koszt",
    "manual_source": "ręcznie wprowadzony",
    "follow_on_source": "scenariusz użytkownika",
    "open": "Otwórz",
    "duplicate": "Utwórz kopię",
    "delete": "Usuń",
    "history_item": "{name} — {modified_at}",
    "history_tooltip": "ID: {id}; utworzono: {created_at}",
    "copy_suffix": "{name} (kopia)",
    "balance_chart_name": "Wykres pozostałego kapitału w PLN",
    "balance_table_name": "Wartości wykresu salda",
    "balance_headers": "Okres|Pozostały kapitał (PLN)|Data",
    "summary_interest": "Łączne odsetki:",
    "summary_charges": "Opłaty kredytowe:",
    "summary_financing_cost": "Koszt finansowania:",
    "summary_lender": "Spłaty kredytodawcy:",
    "summary_cash": "Wypływ rat i kosztów (bez wkładu):",
    "summary_lifetime": "Łączny wypływ nabywcy:",
    "summary_duration": "Czas spłaty / okres umowny:",
    "summary_ltv": "LTV:",
    "summary_acquisition": "Koszt nabycia nieruchomości:",
    "summary_savings": "Oszczędność odsetkowa względem rat bez nadpłat:",
    "summary_nominal_cost": "Całkowity nominalny koszt kredytu:",
    "rate_heading": "Początkowa stopa nominalna / uproszczona efektywna (nie RRSO):",
    "engine_old": (
        "Wynik zapisany przez silnik {version}; otwarto bez ponownego przeliczenia. "
        "Konwencja: {convention}."
    ),
    "engine_current": "Wersja silnika: {version}. Konwencja: {convention}.",
    "save": "Zapisz w historii",
    "schedule_headers": (
        "Okres|Data raty|Stopa nominalna|Odsetki|Kapitał raty|Rata obowiązkowa|"
        "Nadpłata żądana|Nadpłata zastosowana|Koszty|Wypływ|Pozostały kapitał|"
        "Źródło stopy|Pochodzenie stopy"
    ),
    "duration_value": "{effective} / {contractual} miesięcy",
    "calculation_ready": "Obliczenia gotowe",
    "scenario_saved": "Scenariusz zapisany",
    "unsaved_title": "Niezapisane zmiany",
    "open_discard_question": "Odrzucić niezapisane zmiany i otworzyć scenariusz?",
    "open_cancelled": "Otwieranie anulowano, ponieważ formularz zmienił się w międzyczasie",
    "open_failed": "Nie można otworzyć scenariusza: {detail}",
    "scenario_missing": "Nie znaleziono scenariusza",
    "scenario_opened": "Scenariusz otwarty",
    "delete_title": "Usunięcie scenariusza",
    "delete_question": "Czy na pewno usunąć wybrany scenariusz?",
    "scenario_deleted": "Scenariusz usunięty",
    "wait_operation": "Poczekaj na zakończenie bieżącej operacji",
    "close_discard_question": "Zamknąć i porzucić niezapisane zmiany?",
    "monthly_cap_error": "Limit miesięczny jest niższy od wymaganej raty.",
    "extra_period_error": "Okres nadpłaty przekracza okres kredytu.",
    "charge_period_error": "Okres kosztu przekracza okres kredytu.",
    "interest_shortfall_error": "Rata obowiązkowa nie pokrywa odsetek.",
    "cannot_calculate": "Nie można obliczyć scenariusza: {detail}",
    "required_number": "Brak wartości: {name}",
    "invalid_number": "Nieprawidłowa liczba: {name}",
    "invalid_integer": "Nieprawidłowa liczba całkowita: {name}",
    "positive_integer": "{name} musi być dodatni",
    "nonnegative_integer": "{name} nie może być ujemny",
    "invalid_date": "{name}: nieprawidłowa data (RRRR-MM-DD)",
    "rate_requires_user": "wymaga wartości użytkownika",
    "term_not_determinable": "Nie można wyznaczyć okresu",
    "term_formula": "rata równa, stopa i kwota kredytu",
    "payment_conflict": "Wprowadzona rata jest sprzeczna z kwotą, stopą i okresem",
    "payment_requires_fixed": "wymaga stałej stopy i rat równych",
    "invalid_observation_kind": "Rodzaj obserwacji musi być historyczny lub hipotetyczny",
    "missing_first_index": "Brak początkowej wartości indeksu",
    "first_index_conflict": "Indeks początkowy jest sprzeczny z pierwszą obserwacją",
    "name_required": "name: podaj nazwę scenariusza",
    "color_format": "color: wpisz kolor w formacie #RRGGBB",
    "nominal_missing": "Brak stopy nominalnej",
    "periodic_nominal_missing": "Brak początkowej stopy nominalnej",
    "margin_missing": "Brak marży",
    "extra_after_term": "one_time: okres nadpłaty przekracza okres kredytu",
    "charge_after_term": "charges: okres kosztu przekracza okres kredytu",
    "unknown_saved_choice": "Nieznana wartość pola wyboru w zapisanym scenariuszu",
    "invalid_saved_derived": "Nieprawidłowa zapisana wartość wyliczona",
    "invalid_saved_origin": "Nieprawidłowe zapisane pochodzenie wartości",
    "invalid_saved_provenance": "Nieprawidłowe zapisane wyjaśnienie wartości",
    "invalid_saved_state": "Nieprawidłowy zapisany stan formularza",
    "core_conflict": "Sprzeczne wartości: {name}",
    "core_not_cent": "Nie można jednoznacznie wyznaczyć {name} z dokładnością do grosza",
    "core_positive": "Wymagana jest dodatnia wartość pola: {name}",
    "core_nonnegative": "Wartość pola {name} nie może być ujemna",
    "core_outside_range": "Wartość pola {name} jest poza dopuszczalnym zakresem",
    "core_rate_gap": "Brakuje obserwacji stopy dla części okresów",
    "core_historical_missing": "Brakuje historycznej obserwacji stopy",
    "core_negative_rate": "Łączna stopa nominalna nie może być ujemna",
    "core_charge_funding": "Koszt cykliczny musi być opłacany ze środków własnych",
    "core_charge_invalid": "Nieprawidłowa klasyfikacja lub okres kosztu",
    "core_rate_invalid": "Nieprawidłowa konfiguracja stopy procentowej",
    "core_historical_dates": "Obserwacja historyczna wymaga prawidłowych dat",
    "core_historical_late": "Obserwacja stopy nie była dostępna w wymaganym dniu",
    "core_payment_invalid": "Rata nie pokrywa wymaganych zobowiązań",
    "core_term_invalid": "Nieprawidłowy okres kredytu",
    "core_rate_missing": "Brak wymaganej wartości indeksu lub marży",
    "formula_prefix": "Wzór: {formula}",
    "reason_missing": "Za mało niezależnych danych do wyliczenia wartości",
    "formula_annuity": "Rata wyliczona ze wzoru na ratę równą, zaokrąglona do grosza",
    "field_price": "cena",
    "field_down_payment": "wkład własny",
    "field_purchase_loan": "kwota kredytu",
    "field_down_fraction": "udział wkładu",
    "field_ltv": "LTV",
    "field_initial_debt": "początkowe zadłużenie",
    "field_financed_charges": "finansowane koszty",
    "field_nominal_annual": "stopa nominalna",
    "field_index_annual": "wartość indeksu",
    "field_margin": "marża",
    "field_term_months": "okres kredytu",
    "estimate_notice": (
        "LoanSim pokazuje szacunek do porównywania scenariuszy; "
        "rzeczywisty harmonogram banku może się różnić."
    ),
    "rate_source_fixed": "Stała",
    "rate_source_historical": "Historyczna",
    "rate_source_hypothetical": "Hipotetyczna",
    "rate_source_constant_future": "Stała przyszła (założenie)",
}


def tr(key: str, **values: object) -> str:
    """Return current Polish copy from a centralized localization boundary."""
    return PL[key].format(**values)


def tr_list(key: str) -> list[str]:
    """Return a table heading list without hard-coded widget copy."""
    return tr(key).split("|")


_FORMULA_NAMES = {
    key.removeprefix("field_"): value for key, value in PL.items() if key.startswith("field_")
}
_CORE_ERROR_KEYS: dict[str, tuple[str, str | None]] = {
    "monthly cap is below the mandatory payment": ("monthly_cap_error", "monthly_cap"),
    "extra-payment period exceeds contractual term": ("extra_period_error", "one_time"),
    "charge period exceeds contractual term": ("charge_period_error", "charges"),
    "mandatory payment does not cover interest": (
        "interest_shortfall_error",
        "mandatory_installment",
    ),
    "monthly rate path has a missing or duplicate interior observation": (
        "core_rate_gap",
        "rate_path",
    ),
    "missing historical monthly rate": ("core_historical_missing", "rate_path"),
    "negative total nominal rate is unsupported": ("core_negative_rate", "nominal_annual"),
    "total nominal annual rate cannot be negative": ("core_negative_rate", "nominal_annual"),
    (
        "Recurring charges in Phase 1 must be paid from own funds; "
        "financing them with the loan is unsupported"
    ): (
        "core_charge_funding",
        "charges",
    ),
    "historical observation dates are required": ("core_historical_dates", "rate_path"),
    "historical observation postdates publication": ("core_historical_dates", "rate_path"),
    "historical rate was not published by the period start": ("core_historical_late", "rate_path"),
    "historical rate was unavailable at the as-of date": ("core_historical_late", "rate_path"),
    "schedule did not discharge the balance": ("core_payment_invalid", "monthly_cap"),
    "term_months must be a positive integer": ("core_term_invalid", "term_months"),
    "at least one monthly observation is required": ("core_rate_missing", "rate_path"),
}


def localize_core_error(message: str) -> tuple[str, str | None]:
    """Translate deterministic core validation errors at the presentation boundary."""
    exact = _CORE_ERROR_KEYS.get(message)
    if exact is not None:
        return tr(exact[0]), exact[1]
    for suffix, key in (
        (" conflict between supplied and derived values", "core_conflict"),
        (" is not uniquely representable to a cent", "core_not_cent"),
        (" must be positive", "core_positive"),
        (" must be nonnegative", "core_nonnegative"),
        (" is outside the supported range", "core_outside_range"),
    ):
        if message.endswith(suffix):
            field = message[: -len(suffix)]
            name = _FORMULA_NAMES.get(field, field)
            return tr(key, name=name), field
    return message, None


def explain_derived(text: str | None) -> str:
    """Translate stored core formulas only for display; preserve raw provenance."""
    if not text:
        return ""
    if text == "insufficient independent inputs":
        return tr("reason_missing")
    if text == "monthly annuity present-value formula, rounded to cents":
        return tr("formula_annuity")
    formula = re.sub(
        r"\b(?:" + "|".join(map(re.escape, _FORMULA_NAMES)) + r")\b",
        lambda match: _FORMULA_NAMES[match.group()],
        text,
    )
    return tr("formula_prefix", formula=formula)
