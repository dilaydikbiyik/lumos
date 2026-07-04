"""
Behavioral coach — the thing robo-advisors don't do: react to how a
downturn FEELS for this specific person, not just show them a number.

Zero AI cost by default (template-based, keyed on loss_tolerance); an
optional richer AI-generated version is available for the chat surface.
"""
from typing import Optional

from backend.services.ai_service import generate_text

# Calm, profile-specific templates — no AI call needed for the common case
_DROP_MESSAGES = {
    "low": (
        "Piyasada bir düşüş görüyorsun ve bu seni tedirgin edebilir — bu son derece "
        "doğal. Geçmişte benzer düşüşlerin çoğu zamanla toparlandı. Şu an hiçbir şey "
        "yapmana gerek yok; planın zaten bu tür dalgalanmaları hesaba katarak kuruldu."
    ),
    "medium": (
        "Bugünkü düşüş, uzun vadeli planının bir parçası olarak beklenen türden bir "
        "dalgalanma. Elindeki bilgiye göre karar ver, ana haber başlıklarına göre değil."
    ),
    "high": (
        "Düşüş gördün ve belki de bunu bir fırsat olarak değerlendirmeyi "
        "düşünüyorsun — bu senin profiline uygun bir tepki. Yine de acele etme; "
        "planlı hareket, dürtüsel hareketten güçlüdür."
    ),
}

_RISE_MESSAGES = {
    "low": "Piyasa yükseldi — güzel haber, ama bu bir sonraki düşüşte satmak için bir sebep değil. Plana sadık kalmak burada da geçerli.",
    "medium": "Yükseliş iyi gidiyor. Bu, riskini artırmak için bir işaret değil — planın zaten dengeli kurulu.",
    "high": "Yükseliş moralini yükseltebilir, ama aşırı güven riskli kararlara yol açabilir. Disiplin, coşkudan önce gelir.",
}


def drop_message(loss_tolerance: str, drawdown_pct: Optional[float] = None) -> str:
    """Calming, profile-specific message for a market downturn."""
    return _DROP_MESSAGES.get(loss_tolerance, _DROP_MESSAGES["medium"])


def rise_message(loss_tolerance: str) -> str:
    """Grounding message for a market upswing — prevents overconfidence."""
    return _RISE_MESSAGES.get(loss_tolerance, _RISE_MESSAGES["medium"])


def behavior_mirror(stated_loss_tolerance: str, recent_action: str) -> Optional[str]:
    """
    Gently hold up a mirror when stated risk tolerance and actual behavior
    diverge — e.g. profile says "I'd sell everything" but the user just
    bought more during a dip, or vice versa.

    recent_action: "bought_dip" | "sold_dip" | "bought_rise" | "sold_rise"
    """
    mismatches = {
        ("low", "bought_dip"): (
            "Profilinde düşüşlerde tedirgin olduğunu belirtmiştin, ama düşüş "
            "sırasında alım yaptın — bu güzel bir cesaret işareti. Bu deneyimi "
            "not al; belki risk toleransın düşündüğünden yüksek."
        ),
        ("high", "sold_dip"): (
            "Profilinde düşüşleri fırsat olarak gördüğünü belirtmiştin, ama bu "
            "düşüşte sattın. Bu tamamen senin kararın — sadece fark etmeni "
            "istedik, çünkü bazen an içindeki duygu profildeki niyetten farklı olabilir."
        ),
    }
    return mismatches.get((stated_loss_tolerance, recent_action))


def ai_coach_message(loss_tolerance: str, context: str) -> str:
    """
    Richer, situation-specific coaching via the LLM — used when the chat
    surface wants a tailored response rather than a static template.
    """
    system = (
        "You are Lumos's behavioral coach. The user's loss tolerance is "
        f"'{loss_tolerance}' (low/medium/high). Respond in 2-3 calm sentences: "
        "acknowledge the situation, ground them in their own plan, never alarmist, "
        "never dismissive. Respond in the same language as the context."
    )
    return generate_text(context, system=system)
