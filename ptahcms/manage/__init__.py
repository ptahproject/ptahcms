# ptah manage api

from ptahcms.manage.apps import MANAGE_APP_ROUTE
from ptahcms.manage.apps import MANAGE_APP_CATEGORY

# pyramid include
def includeme(config):
    config.add_route(
        MANAGE_APP_ROUTE, '# {0}'.format(MANAGE_APP_ROUTE),
        use_global_views=False)

    # manage layouts
    from ptah.manage.manage import PtahManageRoute, LayoutManage
    from ptah.view import MasterLayout
    from ptahcms.node import Node

    config.add_layout(
        'ptah-manage', PtahManageRoute, route_name=MANAGE_APP_ROUTE,
        renderer='ptahcms.manage:templates/apps-layout.lt', view=LayoutManage,
        use_global_views=False, 
    )

    config.add_layout(
        '', Node, parent='ptah-mange', route_name=MANAGE_APP_ROUTE,
        renderer='ptah-manage:ptah-manage.lt', view=MasterLayout,
        use_global_views=False, 
    )
