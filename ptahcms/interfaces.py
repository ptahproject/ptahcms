""" interfaces """
from zope import interface
from pyramid.httpexceptions import HTTPServerError

from ptah import form
from ptah.interfaces import TypeException, Forbidden, NotFound


class Error(HTTPServerError, TypeException):
    """ internale error """


class INode(interface.Interface):
    """ base """

    __id__ = interface.Attribute('Id')
    __uri__ = interface.Attribute('Uri')
    __type_id__ = interface.Attribute('Node type')
    __parent_uri__ = interface.Attribute('Node parent')


class IContent(interface.Interface):
    """ base interface """

    name = interface.Attribute('Name')


class IContainer(IContent):
    """ base container content """

    __path__ = interface.Attribute('traversal path')


class IApplicationPolicy(interface.Interface):
    """ application policy """


class IApplicationRoot(interface.Interface):
    """ application root object """

    __root_path__ = interface.Attribute('Current mount point')


class IApplicationRootFactory(interface.Interface):
    """ application root factory """

    def __call__(**kw):
        """ return ApplicationRoot object """


class IBlob(INode):
    """ blob """

    mimetype = interface.Attribute('Blob mimetype')
    filename = interface.Attribute('Original filename')
    data = interface.Attribute('Blob data')


class IBlobStorage(interface.Interface):
    """ blob storage """

    def add(parent, data, mimetype=None, filename=None):
        """ add blob return uri """

    def query(uri):
        """ return blob object """

    def replace(uri, data, mimetype=None, filename=None):
        """ replace existing blob """

    def remove(uri):
        """ remove blob """


ContentSchema = form.Fieldset(

    form.TextField(
        name = 'title',
        title = 'Title'),

    form.TextAreaField(
        name = 'description',
        title = 'Description',
        missing = ''),
    )


class SpecialSymbolsValidator(form.Regex):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Forbidden characters"

        super(SpecialSymbolsValidator, self).__init__(
            '^[a-z0-9-]+$', msg=msg)


ContentNameSchema = form.Fieldset(

    form.TextField(
        name = '__name__',
        title = 'Name',
        description = 'Name is the part that shows up in '\
                      'the URL. Allowed character are "a-z", "0-9" and "-".',
        validator = SpecialSymbolsValidator())
    )
