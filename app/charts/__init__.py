from .plot_weekly_by_city import get_weekly_by_city_plot
from .plot_monthly_total import get_monthly_total_plot   # 👈 добавить импорт

CHARTS = {
    "weekly_by_city": lambda **kwargs: get_weekly_by_city_plot(city_name=kwargs.get("city", "Москва")),
    "monthly_total": lambda **kwargs: get_monthly_total_plot(),  # 👈 добавить
}
