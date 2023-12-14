from app.plug import *

@Plug.register("_barchart")
class BaseBarChart(UIPlugin):

    def process(self, data:dict, title='Bar Chart', **kwargs):
        x_axis = list(data.keys())
        y_axis = list(data.values())
        bar_groups = []
        for i in range(len(x_axis)):
            bar_groups.append(ft.BarChartGroup(
                x=i,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=y_axis[i],
                        width=40,
                        tooltip=y_axis[i],
                        border_radius=0,
                    ),
                ],
            ))
        labels = [ft.ChartAxisLabel(
            value=idx, label=ft.Container(ft.Text(item), padding=10)
        ) for idx, item in enumerate(x_axis)]
        return ft.BarChart(
            bar_groups=bar_groups,
            bottom_axis=ft.ChartAxis(
                labels=labels,
                labels_size=40,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.colors.GREY_300, width=1, dash_pattern=[3, 3]
            ),
            left_axis=ft.ChartAxis(
                labels_size=40, 
                title=ft.Text(title),
                title_size=20
            ),
            tooltip_bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            max_y=int(max(y_axis) / 0.9),
            interactive=True,
            expand=True,
            )


@Plug.register("_linechart")
class BaseLineChart(UIPlugin):
    """
    data: {
        line1: [(0.5, 1), (1, 2)],
        line2: ...
    }
    """
    def process(self, data:dict, **kwargs):
        labels = [
            ft.ChartAxisLabel(
                value=idx+1,
                label=ft.Container(
                    ft.Text(
                        name,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                    ),
                    margin=ft.margin.only(top=10),
                ),
            )
        for idx, name in enumerate(list(data.keys()))]
        series = []
        for name, values in data.items():
            points = [ft.LineChartDataPoint(i[0], i[1]) for i in values]
            series.append(
                ft.LineChartData(
                    data_points=points,
                    stroke_width=5,
                    color=ft.colors.CYAN,
                    curved=True,
                    stroke_cap_round=True,
                )
            )
        return ft.LineChart(
            data_series=series,
            border=ft.border.all(3, ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE)),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1, color=ft.colors.with_opacity(0.2, ft.colors.ON_SURFACE), width=1
            ),
            bottom_axis=ft.ChartAxis(labels=labels),
            expand=True
        )
            
@Plug.register("Linechart")
class BaseBarChart(UIPlugin):

    def process(self, data:dict, **kwargs):
        data = dict(apple=[(1, 30), (2, 40), (3, 50), (4, 20), (5, 10)],
                    bogo=[(1, 15), (2, 25), (3, 40), (4, 10)])
        return Plug.run(plugins=("_linechart",), data=data, **kwargs)