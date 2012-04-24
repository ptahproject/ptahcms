# ptah manage api

from ptahcms.manage.apps import MANAGE_APP_ROUTE
from ptahcms.manage.apps import MANAGE_APP_CATEGORY


# pyramid include
def includeme(config):
    config.add_route(
        MANAGE_APP_ROUTE, '# {0}'.format(MANAGE_APP_ROUTE),
        use_global_views=False)
