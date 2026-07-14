from .models import Category, Hotspot


ACCOUNT_BY_CATEGORY: dict[Category, int] = {
    Category.SOCIAL: 1,
    Category.LEGAL: 2,
    Category.MONEY: 3,
    Category.INTERNATIONAL: 4,
    Category.PEOPLE: 5,
}


def route_account(
    hotspot: Hotspot,
    performance_by_account: dict[int, float],
) -> int:
    categories = (hotspot.category, *hotspot.secondary_categories)
    candidates = tuple(dict.fromkeys(ACCOUNT_BY_CATEGORY[item] for item in categories))
    return max(
        candidates,
        key=lambda account: (
            performance_by_account.get(account, 0.0),
            account == ACCOUNT_BY_CATEGORY[hotspot.category],
        ),
    )
