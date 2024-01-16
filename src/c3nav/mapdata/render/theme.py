from c3nav.mapdata.models import LocationGroup
from c3nav.mapdata.models.geometry.space import ObstacleGroup
from c3nav.mapdata.models.theme import Theme

RENDER_COLOR_BACKGROUND = "#DCDCDC"
RENDER_COLOR_WALL_FILL = "#aaaaaa"
RENDER_COLOR_WALL_BORDER = "#666666"
RENDER_COLOR_DOOR_FILL = "#ffffff"
RENDER_COLOR_GROUND_FILL = "#eeeeee"
RENDER_COLOR_OBSTACLES_DEFAULT_FILL = "#b7b7b7"
RENDER_COLOR_OBSTACLES_DEFAULT_BORDER = "#888888"


class ThemeColorManager:
    # TODO: border colors are not implemented yet?
    def __init__(self, theme: Theme = None):
        if theme is None:
            self.background = RENDER_COLOR_BACKGROUND
            self.wall_fill = RENDER_COLOR_WALL_FILL
            self.wall_border = RENDER_COLOR_WALL_BORDER
            self.door_fill = RENDER_COLOR_DOOR_FILL
            self.ground_fill = RENDER_COLOR_GROUND_FILL
            self.obstacles_default_fill = RENDER_COLOR_OBSTACLES_DEFAULT_FILL
            self.obstacles_default_border = RENDER_COLOR_OBSTACLES_DEFAULT_BORDER
            self.location_group_border_colors = {}
            self.location_group_fill_colors = {
                l.pk: l.color
                for l in LocationGroup.objects.filter(color__isnull=False).all()
            }
            self.obstacle_group_border_colors = {}
            self.obstacle_group_fill_colors = {
                o.pk: o.color
                for o in ObstacleGroup.objects.filter(color__isnull=False).all()
            }
        else:
            self.background = theme.color_background
            self.wall_fill = theme.color_wall_fill
            self.wall_border = theme.color_wall_border
            self.door_fill = theme.color_door_fill
            self.ground_fill = theme.color_ground_fill
            self.obstacles_default_fill = theme.color_obstacles_default_fill
            self.obstacles_default_border = theme.color_obstacles_default_border
            self.location_group_border_colors = {
                l.location_group_id: l.border_color
                for l in theme.location_groups.all()
            }
            self.location_group_fill_colors = {
                l.location_group_id: l.fill_color
                for l in theme.location_groups.all()
            }
            self.obstacle_group_border_colors = {
                o.obstacle_group_id: o.border_color
                for o in theme.obstacle_groups.all()
            }
            self.obstacle_group_fill_colors = {
                o.obstacle_group_id: o.fill_color
                for o in theme.obstacle_groups.all()
            }

    def locationgroup_border_color(self, location_group: LocationGroup):
        return self.location_group_border_colors.get(location_group.pk, None)

    def locationgroup_fill_color(self, location_group: LocationGroup):
        return self.location_group_fill_colors.get(location_group.pk, None)

    def obstaclegroup_border_color(self, obstacle_group: ObstacleGroup):
        return self.obstacle_group_border_colors.get(obstacle_group.pk, self.obstacles_default_border)

    def obstaclegroup_fill_color(self, obstacle_group: ObstacleGroup):
        return self.obstacle_group_fill_colors.get(obstacle_group.pk, self.obstacles_default_fill)


class ColorManager:
    themes = {}
    default_theme = None

    @classmethod
    def for_theme(cls, theme):
        if theme is None:
            if cls.default_theme is None:
                cls.default_theme = ThemeColorManager()
            return cls.default_theme
        if not isinstance(theme, Theme):
            theme = Theme.objects.get(pk=theme)
        if theme.pk not in cls.themes:
            cls.themes[theme.pk] = ThemeColorManager(theme)
        return cls.themes[theme.pk]

    @classmethod
    def refresh(cls):
        cls.themes.clear()