from .plot_monthly_total import get_monthly_total_plot
from .plot_weekly_by_city import get_weekly_by_city_plot
from .plot_top10_regions_bar import get_top10_regions_bar_plot
from .plot_global_duration_min import get_global_duration_min

CHARTS = {
    "weekly_by_city": lambda **kwargs: get_weekly_by_city_plot(city_name=kwargs.get("city", "Москва")),
    "monthly_total": lambda **kwargs: get_monthly_total_plot(),  # 👈 добавить
    "top10_regions": lambda **kwargs: get_top10_regions_bar_plot(),
}


