
from .plot_weekly_by_city import get_weekly_by_city_plot
#from .plot_top10_regions_pie import get_top10_regions_pie_plot
#from .plot_city_monthly_trend import get_city_monthly_trend_plot
#from .plot_hourly_dayparts import get_hourly_dayparts_plot


CHARTS = {

    "weekly_by_city": lambda **kwargs: get_weekly_by_city_plot(city_name=kwargs.get("city", "Москва")),
    #"top10_regions": lambda **kwargs: get_top10_regions_pie_plot(),
    #"city_monthly_trend": lambda **kwargs: get_city_monthly_trend_plot(city_name=kwargs.get("city", "Москва")),
    #"hourly_dayparts": lambda **kwargs: get_hourly_dayparts_plot(),
}
