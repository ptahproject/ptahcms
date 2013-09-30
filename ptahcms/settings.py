import ptah
from ptahcms import form
import translationstring

_ = translationstring.TranslationStringFactory('ptahcms')

CFG_ID_CMS = 'ptahcms'


ptah.register_settings(
    CFG_ID_CMS,

    form.TextField(
        name = 'brand-name',
        title = _('Brand name'),
        description = _('Name of your site.'),
        default = 'Ptah CMS'),

    title = 'Ptah cms settings',
    )
