""" content helper forms """
import re
import unicodedata
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound

from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

import ptah
from ptahcms import form
from ptahcms.security import wrap
from ptahcms.interfaces import ContentNameSchema, IApplicationRoot, IContainer
from ptahcms.settings import _


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
    def tinfo(self):
        tname = self.request.params.get('tname', None)
        if not tname:
            raise HTTPNotFound()
        tinfo = ptah.resolve('type:%s' % tname)

        if not tinfo:
            raise HTTPNotFound()
        if not tinfo in self.context.__type__.list_types(self.context):
            raise HTTPForbidden()

        return tinfo

    @reify
    def fields(self):
        return self.tinfo.fieldset

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
                error = form.Invalid(_('Name already in use'))
                error.field = self.widgets['__name__']
                errors.append(error)

    def create(self, **data):
        name = data.get('__name__')
        if not name:
            name = self.chooseName(**data)

        return wrap(self.container).create(
            self.tinfo.__uri__, name, **data)

    @form.button(_('Add'), actype=form.AC_PRIMARY)
    def add_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        content = self.create(**data)

        self.request.add_message(_('New content has been created.'), 'success')
        return HTTPFound(location=self.get_next_url(content))

    @form.button(_('Cancel'))
    def cancel_handler(self):
        return HTTPFound(location='.')

    def get_next_url(self, content):
        return self.request.resource_url(content)


class EditForm(form.Form):

    def __init__(self, context, request):
        self.tinfo = context.__type__

        super(EditForm, self).__init__(context, request)

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

    @form.button(_('Save'), actype=form.AC_PRIMARY)
    def save_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        self.apply_changes(**data)

        self.request.add_message(_('Changes have been saved.', 'success'))
        return HTTPFound(location=self.get_next_url())

    @form.button(_('Cancel'))
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

    def form_content(self):
        data = {}
        for name, field in self.fields.items():
            data[name] = getattr(self.context, name, field.default)

        return data

    def update(self):
        if IApplicationRoot.implementedBy(self.tinfo.cls):
            self.request.add_message(_('You can not rename Applications.'), 'info')
            return self.cancel_handler()
        return super(RenameForm, self).update()

    def validate(self, data, errors):
        super(RenameForm, self).validate(data, errors)

        name = data['__name__']
        if name != self.context.__name__:
            if self.container and name in self.container.keys():
                error = form.Invalid(_('Name already in use'))
                error.field = self.widgets['__name__']
                errors.append(error)

    def apply_changes(self, **data):
        name = data.get('__name__')
        return wrap(self.context).rename(name, **data)

    @form.button(_('Rename'), actype=form.AC_PRIMARY)
    def add_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        content = self.apply_changes(**data)

        self.request.add_message(_('Content has been renamed.'), 'success')
        return HTTPFound(location=self.get_next_url(content))

    @form.button(_('Cancel'))
    def cancel_handler(self):
        return HTTPFound(location='.')

    def get_next_url(self, content):
        return self.request.resource_url(content)


class DeleteForm(form.Form):
    klass=""

    def __init__(self, context, request):
        self.tinfo = context.__type__
        super(DeleteForm, self).__init__(context, request)

    def update(self):
        if IApplicationRoot.implementedBy(self.tinfo.cls):
            self.request.add_message(_('You can not delete Applications.'), 'info')
            return self.cancel_handler()
        return super(DeleteForm, self).update()

    def apply_changes(self):
        wrap(self.context).delete()

    def validate(self, data, errors):
        super(DeleteForm, self).validate(data, errors)

        if IContainer.implementedBy(self.context.__type__.cls) and self.context.values():
            error = form.Invalid(msg=_('This folder is not empty.'))
            errors.append(error)

    @form.button(_('Delete'), actype=form.AC_DANGER)
    def save_handler(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        self.apply_changes()
        self.request.add_message(_("Content has been removed."), 'success')
        return HTTPFound(location='..')

    @form.button(_('Cancel'))
    def cancel_handler(self):
        return HTTPFound(location=self.get_cancel_url())

    def get_cancel_url(self):
        return self.request.resource_url(self.context)


class ShareForm(form.Form):

    csrf = True

    bsize = 15
    term = ''

    def __init__(self, context, request):
        self.tinfo = context.__type__
        self.roles = [r for r in ptah.get_roles().values() if not r.system]
        self.local_roles = local_roles = context.__local_roles__
        self.local_principals = [ptah.resolve(principalUri)
                               for principalUri in self.local_roles]

        for p in list(ptah.search_principals('')):
            p = ptah.resolve(p.__uri__)
            if hasattr(p, 'properties'):
                if p.properties.get('roles') and p not in self.local_principals:
                    self.local_principals.append(p)

        self.principals = sorted(self.local_principals, key=lambda p: str(p))

        super(ShareForm, self).__init__(context, request)

    def get_global_roles(self, principal):
        return principal.properties.get('roles', []) if hasattr(principal, 'properties') else []

    def update(self):
        if 'form.buttons.search' in self.request.POST:
            self.term = self.request.POST.get('term')
            self.principals = list(ptah.search_principals(self.term))

        if 'form.buttons.clear' in self.request.POST:
            self.term = ''
            self.principals = self.local_principals

        if not self.principals:
            if not self.term:
                self.request.add_message(_('There are no local roles defined.'), 'info')
            else:
                self.request.add_message(_('There are no users or groups found.'), 'info')

        return super(ShareForm, self).update()

    @form.button(_('Save'), actype=form.AC_PRIMARY)
    def save(self):
        users = []
        userdata = {}
        local_roles = self.context.__local_roles__
        for attr, val in self.request.POST.items():
            if attr.startswith('user-'):
                userId, roleId = attr[5:].rsplit('-',1)
                data = userdata.setdefault(str(userId), [])
                data.append(str(roleId))
            if attr.startswith('userid-'):
                users.append(str(attr.split('userid-')[-1]))

        for uid in users:
            if userdata.get(uid):
                local_roles[str(uid)] = userdata[uid]
            elif uid in local_roles:
                del local_roles[uid]

        self.context.__local_roles__ = local_roles
        self.request.add_message(_('Changes have been saved.'), 'success')
        return HTTPFound(location=self.request.resource_url(self.context))

    @form.button(_('Cancel'))
    def cancel_handler(self):
        return HTTPFound(location=self.get_next_url())

    def get_next_url(self):
        return '.'


class ContactForm(form.Form):

    fields = form.Fieldset(
        form.TextField(
            'name', title=_('Full Name')),
        form.TextField(
            'sender', title=_('E-Mail Address'),
            validator=form.Email()),
        form.TextField(
            'subject', title=_('Sebject')),
        form.TextAreaField(
            'body', title=_('Your message'), default='')
    )

    def mail_submission(self, data):
        mailer = get_mailer(self.request)
        sender = '%s <%s>' % (data['name'], data['sender'])
        recipients = [mailer.default_sender]
        subject = data['subject']
        body = data['body']
        message = Message(subject, recipients=recipients, body=body,
            html=None, sender=sender, cc=None, bcc=[data['sender']],
            extra_headers=None, attachments=None)
        mailer.send(message)

    @form.button(_('Send'), actype=form.AC_PRIMARY)
    def send_msg(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return
        try:
            self.mail_submission(data)
            self.request.add_message(
                _("Your message has been sent. "
                  "You can find a copy of it in your mailbox."), 'success')
            return HTTPFound(location=self.request.path_url)
        except:
            self.request.add_message(
            _("""Oops, your message could not be sent."""), 'error')
            return
