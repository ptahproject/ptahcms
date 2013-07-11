""" content helper forms """
import re
import unicodedata
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah
from ptahcms import form
from ptahcms.security import wrap
from ptahcms.interfaces import ContentNameSchema, IApplicationRoot


class AddForm(form.Form):

    tinfo = None
    container = None

    name_show = False
    name_suffix = ''
    name_fields = ContentNameSchema

    def __init__(self, context, request):
        self.container = context
        super(AddForm, self).__init__(context, request)

    @reify
    def fields(self):
        return self.tinfo.fieldset

    @reify
    def label(self):
        return 'Add %s'%self.tinfo.title

    @reify
    def description(self):
        return self.tinfo.description

    def chooseName(self, **kw):
        name = kw.get('title', '')

        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
        name = re.sub(
            '-{2,}', '-',
            re.sub('^\w-|-\w-|-\w$', '-',
                   re.sub(r'\W', '-', name.strip()))).strip('-').lower()

        suffix = self.name_suffix
        n = '%s%s'%(name, suffix)
        i = 0
        while n in self.container:
            i += 1
            n = '%s-%s%s'%(name, i, suffix)

        return n.replace('/', '-').lstrip('+@')

    def update(self):
        self.name_suffix = getattr(self.tinfo, 'name_suffix', '')

        self.tinfo.check_context(self.container)
        return super(AddForm, self).update()

    def update_widgets(self):
        if self.name_show and not self.fields.get('__name__'):
            self.fields.append(self.name_fields)
        super(AddForm, self).update_widgets()

    def validate(self, data, errors):
        super(AddForm, self).validate(data, errors)

        if self.name_show and '__name__' in data and data['__name__']:
            name = data['__name__']
            if name in self.container.keys():
                error = form.Invalid('Name already in use')
                error.field = self.widgets['__name__']
                errors.append(error)

    def create(self, **data):
        name = data.get('__name__')
        if not name:
            name = self.chooseName(**data)

        return wrap(self.container).create(
            self.tinfo.__uri__, name, **data)

    @form.button('Add', actype=form.AC_PRIMARY)
    def add_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        content = self.create(**data)

        self.request.add_message('New content has been created.', 'success')
        return HTTPFound(location=self.get_next_url(content))

    @form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location='.')

    def get_next_url(self, content):
        return self.request.resource_url(content)


class EditForm(form.Form):

    def __init__(self, context, request):
        self.tinfo = context.__type__

        super(EditForm, self).__init__(context, request)

    @reify
    def label(self):
        return 'Modify content: %s'%self.tinfo.title

    @reify
    def fields(self):
        return self.tinfo.fieldset

    def form_content(self):
        data = {}
        for name, field in self.tinfo.fieldset.items():
            data[name] = getattr(self.context, name, field.default)

        return data

    def apply_changes(self, **data):
        wrap(self.context).update(**data)

    @form.button('Save', actype=form.AC_PRIMARY)
    def save_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        self.apply_changes(**data)

        self.request.add_message('Changes have been saved.', 'success')
        return HTTPFound(location=self.get_next_url())

    @form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location=self.get_next_url())

    def get_next_url(self):
        return '.'


class RenameForm(form.Form):

    tinfo = None
    container = None

    fields = ContentNameSchema

    def __init__(self, context, request):
        self.container = context.__parent_ref__
        self.tinfo = context.__type__
        super(RenameForm, self).__init__(context, request)

    @reify
    def label(self):
        return 'Rename %s'%self.tinfo.title

    @reify
    def description(self):
        return self.tinfo.description

    def form_content(self):
        data = {}
        for name, field in self.fields.items():
            data[name] = getattr(self.context, name, field.default)

        return data

    def update(self):
        if IApplicationRoot.implementedBy(self.tinfo.cls):
            self.request.add_message('You can not rename ApplicationRoot.', 'info')
            return self.cancel_handler()
        return super(RenameForm, self).update()

    def validate(self, data, errors):
        super(RenameForm, self).validate(data, errors)

        name = data['__name__']
        if name != self.context.__name__:
            if self.container and name in self.container.keys():
                error = form.Invalid('Name already in use')
                error.field = self.widgets['__name__']
                errors.append(error)

    def apply_changes(self, **data):
        name = data.get('__name__')
        return wrap(self.context).rename(name, **data)

    @form.button('Rename', actype=form.AC_PRIMARY)
    def add_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        content = self.apply_changes(**data)

        self.request.add_message('Content has been renamed.', 'success')
        return HTTPFound(location=self.get_next_url(content))

    @form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location='.')

    def get_next_url(self, content):
        return self.request.resource_url(content)


class DeleteForm(form.Form):

    def __init__(self, context, request):
        self.tinfo = context.__type__
        super(DeleteForm, self).__init__(context, request)

    @reify
    def label(self):
        return 'Delete %s'%self.tinfo.title

    @reify
    def description(self):
        return 'Are you sure you want to delete "%s"?'%self.context.title

    def update(self):
        if IApplicationRoot.implementedBy(self.tinfo.cls):
            self.request.add_message('You can not delete ApplicationRoot.', 'info')
            return self.cancel_handler()
        return super(DeleteForm, self).update()

    def apply_changes(self):
        wrap(self.context).delete()

    def validate(self, data, errors):
        super(DeleteForm, self).validate(data, errors)

        if self.context.__children__:
            error = form.Invalid(msg='Items found that depends on this content.')
            errors.append(error)

    @form.button('Delete', actype=form.AC_DANGER)
    def save_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        self.apply_changes()
        self.request.add_message("Content has been removed.", 'success')
        return self.get_next_url()

    @form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location=self.request.resource_url(self.context))

    def get_next_url(self):
        return HTTPFound(location='../')

