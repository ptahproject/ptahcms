import transaction
import ptah
from ptah.testing import PtahTestCase

import ptahcms


class TestNode(PtahTestCase):

    def test_node_ctor(self):
        import ptahcms

        # it not possible to instatiate Node
        self.assertRaises(TypeError, ptahcms.Node)

    def test_node(self):
        import ptahcms

        class MyContent(ptahcms.Node):
            __uri_factory__ = ptah.UriFactory('test')

        content = MyContent()
        _uri = content.__uri__
        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == _uri).one()

        self.assertTrue(isinstance(c, ptahcms.Node))
        self.assertIs(ptah.get_session().object_session(c), c.get_session())

    def test_polymorphic_node(self):
        import ptahcms

        class MyContent(ptahcms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        content = MyContent()
        _uri = content.__uri__
        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == _uri).one()

        self.assertTrue(isinstance(c, MyContent))

    def test_node_parent(self):
        import ptahcms

        class MyContent(ptahcms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        parent = MyContent()
        parent_uri = parent.__uri__

        content = MyContent(__parent__ = parent)
        __uri = content.__uri__

        ptah.get_session().add(parent)
        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()

        self.assertTrue(c.__parent_uri__ == parent_uri)
        self.assertTrue(c.__parent_ref__.__uri__ == parent_uri)

    def test_node_local_roles(self):
        import ptah

        class MyContent(ptahcms.Node):
            __uri_factory__ = ptah.UriFactory('test')
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}

        content = MyContent()
        __uri = content.__uri__

        self.assertTrue(ptah.ILocalRolesAware.providedBy(content))

        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()

        c.__local_roles__['userid'] = ('role:1',)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()
        self.assertTrue(c.__local_roles__ == {'userid': ['role:1']})

    def test_node_owners(self):
        import ptah

        class MyContent(ptahcms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        content = MyContent()
        __uri = content.__uri__

        self.assertTrue(ptah.IOwnersAware.providedBy(content))

        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()

        c.__owner__ = 'userid'
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()
        self.assertTrue(c.__owner__ == 'userid')

    def test_node_permissions(self):
        import ptah

        class MyContent(ptahcms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_factory__ = ptah.UriFactory('test')

        content = MyContent()
        __uri = content.__uri__

        self.assertTrue(ptah.IACLsAware.providedBy(content))

        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()

        c.__acls__.append('map1')
        transaction.commit()

        c = ptah.get_session().query(ptahcms.Node).filter(
            ptahcms.Node.__uri__ == __uri).one()
        self.assertTrue(c.__acls__ == ['map1'])
