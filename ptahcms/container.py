""" Base container class implementation """
import sqlalchemy as sqla
from zope.interface import implementer
from pyramid.compat import string_types
from pyramid.threadlocal import get_current_registry

import ptah
from ptahcms.node import load_parents
from ptahcms.content import Content, BaseContent
from ptahcms.security import action
from ptahcms.permissions import View, DeleteContent, RenameContent
from ptahcms.interfaces import IContent, IContainer, NotFound, Error


class BaseContainer(BaseContent):
    """ Content container implementation. """

    _sql_keys = ptah.QueryFreezer(
        lambda: ptah.get_session().query(BaseContent.__name_id__)
            .filter(BaseContent.__parent_uri__ == sqla.sql.bindparam('uri')))

    _sql_values = ptah.QueryFreezer(
        lambda: ptah.get_session().query(BaseContent)
            .filter(BaseContent.__parent_uri__ == sqla.sql.bindparam('uri')))

    def keys(self):
        """Return an list of the keys in the container."""
        return [k for k, in self._sql_keys.all(uri=self.__uri__)]

    def get(self, key, default=None):
        """Get a value for a key

        The default is returned if there is no value for the key.
        """
        item = self._sql_get_in_parent.first(key=key, parent=self.__uri__)
        if item is not None:
            item.__parent__ = self
        return item

    def values(self):
        """Return an list of the values in the container."""

        values = []

        for item in self._sql_values.all(uri = self.__uri__):
            item.__parent__ = self
            values.append(item)

        return values

    def items(self):
        """Return the items of the container."""
        for item in self.values():
            yield item.__name__, item

    def __contains__(self, key):
        """Tell if a key exists in the mapping."""
        return key in self.keys()

    def __getitem__(self, key):
        """Get a value for a key

        A KeyError is raised if there is no value for the key.
        """
        try:
            item = self._sql_get_in_parent.one(key=key, parent=self.__uri__)
            item.__parent__ = self

            return item
        except sqla.orm.exc.NoResultFound:
            raise KeyError(key)

    def __setitem__(self, key, item):
        """Set a new item in the container."""

        if not isinstance(item, BaseContent):
            raise ValueError("Content object is required")

        if item.__uri__ == self.__uri__:
            raise ValueError("Can't set to it self")

        parents = [p.__uri__ for p in load_parents(self)]
        if item.__uri__ in parents:
            raise TypeError("Can't itself to chidlren")

        if key in self.keys():
            raise KeyError(key)

        if item.__parent_uri__ is None:
            event = ptah.events.ContentAddedEvent(item)
        else:
            event = ptah.events.ContentMovedEvent(item)

        item.__name__ = key
        item.__parent__ = self
        item.__parent_uri__ = self.__uri__
        item.__path__ = '%s%s/'%(self.__path__, key)

        Session = ptah.get_session()
        if item not in Session and not ptah.get_session().object_session(item):
            Session.add(item)

        # recursevly update children paths
        def update_path(container):
            path = container.__path__
            for item in container.values():
                item.__path__ = '%s%s/'%(path, item.__name__)

                if isinstance(item, BaseContainer):
                    update_path(item)

        if isinstance(item, BaseContainer):
            update_path(item)

        get_current_registry().notify(event)

    def __delitem__(self, item, flush=True):
        """Delete a value from the container using the key."""

        if isinstance(item, string_types):
            item = self[item]

        if item.__parent_uri__ == self.__uri__:
            if isinstance(item, BaseContainer):
                for key in item.keys():
                    item.__delitem__(key, False)

            get_current_registry().notify(
                ptah.events.ContentDeletingEvent(item))

            Session = ptah.get_session().object_session(item)
            if item in Session:
                try:
                    Session.delete(item)
                    if flush:
                        Session.flush()
                except:
                    pass

            return

        raise KeyError(item)

    @action
    def create(self, tname, name=None, **params):
        tinfo = ptah.resolve(tname)
        if tinfo is None:
            raise NotFound('Type information is not found')

        tinfo.check_context(self)

        item = tinfo.create()

        if not name:
            name = item.__uri__

        if '/' in name:
            raise Error("Names cannot contain '/'")

        if name.startswith(' '):
            raise Error("Names cannot starts with ' '")

        if name in self:
            raise Error("Name already in use.")

        self[name] = item

        item.update(**params)

        return item

    @action(permission=DeleteContent)
    def batchdelete(self, uris):
        """Batch delete"""
        raise NotImplements() # pragma: no cover

    def contents(self):
        """ Returns public or viewable content of the container """
        for content in self.values():
            if IContent.providedBy(content):
                if content.public or ptah.check_permission(View, content):
                    yield content

    def info(self):
        info = super(BaseContainer, self).info()
        info['__container__'] = True
        return info


@implementer(IContainer)
class Container(BaseContainer, Content):
    """ container for content, it just for inheritance """
