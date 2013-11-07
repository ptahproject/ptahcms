# ptahcms api

import pform as form

#
from ptahcms.security import wrap, action
from ptahcms.interfaces import Error, NotFound, Forbidden

# base content classes
from ptahcms.node import Node
from ptahcms.node import load
from ptahcms.node import load_parents
from ptahcms.node import get_policy, set_policy

from ptahcms.content import Content
from ptahcms.content import BaseContent
from ptahcms.container import Container
from ptahcms.container import BaseContainer

# type information
from ptahcms.tinfo import Type

# application root
from ptahcms.root import get_app_factories
from ptahcms.root import BaseApplicationRoot
from ptahcms.root import ApplicationRoot
from ptahcms.root import ApplicationPolicy
from ptahcms.root import ApplicationFactory

# content traverser
from ptahcms.traverser import ContentTraverser

# blob storage
from ptahcms.blob import blob_storage
from ptahcms.interfaces import IBlob
from ptahcms.interfaces import IBlobStorage

# schemas
from ptahcms.interfaces import ContentSchema
from ptahcms.interfaces import ContentNameSchema

# interfaces
from ptahcms.interfaces import INode
from ptahcms.interfaces import IContent
from ptahcms.interfaces import IContainer
from ptahcms.interfaces import IApplicationRoot
from ptahcms.interfaces import IApplicationPolicy

# permissions
from ptahcms.permissions import View
from ptahcms.permissions import AddContent
from ptahcms.permissions import DeleteContent
from ptahcms.permissions import ModifyContent
from ptahcms.permissions import RenameContent
from ptahcms.permissions import ShareContent
from ptah import NOT_ALLOWED
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import NO_PERMISSION_REQUIRED

# rest api
from ptahcms.restsrv import RestService

# cms rest
from ptahcms.rest import restaction

# content add/edit form helpers
from ptahcms.forms import AddForm
from ptahcms.forms import EditForm
from ptahcms.forms import RenameForm
from ptahcms.forms import DeleteForm
from ptahcms.forms import ShareForm
from ptahcms.forms import ContactForm


def includeme(cfg):
    # ptah rest api directive
    from ptahcms import restsrv
    cfg.add_directive('ptah_init_rest', restsrv.enable_rest_api)

    # templates
    cfg.add_layer('ptahcms', path='ptahcms:templates/ptahcms')

    cfg.include('ptahcms.manage')
    cfg.scan()
