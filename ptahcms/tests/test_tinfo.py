import transaction
import sqlalchemy as sqla
import ptah
from ptah import config, form
from ptah.testing import PtahTestCase
from pyramid.httpexceptions import HTTPForbidden
from pyramid.exceptions import ConfigurationConflictError


class TestTypeInfo(PtahTestCase):

    _init_auth = True
    _init_ptah = False
    _includes = ('ptahcms',)

    def test_tinfo(self):
        import ptahcms

        global MyContent
        class MyContent(ptahcms.Content):

            __type__ = ptahcms.Type('mycontent', 'MyContent')

        self.init_ptah()

        all_types = ptah.get_types()

        self.assertTrue('type:mycontent' in all_types)

        tinfo = ptah.get_type('type:mycontent')

        self.assertEqual(tinfo.__uri__, 'type:mycontent')
        self.assertEqual(tinfo.name, 'mycontent')
        self.assertEqual(tinfo.title, 'MyContent')
        self.assertEqual(tinfo.cls, MyContent)

    def test_tinfo_title(self):
        import ptahcms

        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent')

        self.assertEqual(MyContent.__type__.title, 'Mycontent')

        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent', 'MyContent')

        self.assertEqual(MyContent.__type__.title, 'MyContent')

    def test_tinfo_checks(self):
        import ptahcms

        global MyContent, MyContainer
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptahcms.Container):
            __type__ = ptahcms.Type('mycontainer', 'Container')
        self.init_ptah()

        content = MyContent()
        container = MyContainer()

        # always fail
        self.assertFalse(MyContent.__type__.is_allowed(content))
        self.assertRaises(
            HTTPForbidden, MyContent.__type__.check_context, content)

        #
        self.assertTrue(MyContent.__type__.is_allowed(container))
        self.assertEqual(MyContent.__type__.check_context(container), None)

        # permission
        MyContent.__type__.permission = 'Protected'
        self.assertFalse(MyContent.__type__.is_allowed(container))
        self.assertRaises(
            HTTPForbidden, MyContent.__type__.check_context, container)

    def test_tinfo_list(self):
        import ptahcms

        global MyContent, MyContainer
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptahcms.Container):
            __type__ = ptahcms.Type('mycontainer', 'Container')
        self.init_ptah()

        content = MyContent()
        container = MyContainer()

        self.assertEqual(MyContent.__type__.list_types(content), ())
        self.assertEqual(MyContent.__type__.list_types(container), ())

        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

        MyContent.__type__.global_allow = False
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        MyContent.__type__.global_allow = True
        MyContent.__type__.permission = 'Protected'
        self.assertEqual(MyContainer.__type__.list_types(container), [])

    def test_tinfo_global_allow_Node(self):
        import ptahcms

        global MyContent
        class MyContent(ptahcms.Node):
            __type__ = ptahcms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptahcms.Node):
            __type__ = ptahcms.Type('mycontainer', 'Container',
                                     global_allow = True)
        self.init_ptah()

        self.assertFalse(MyContent.__type__.global_allow)
        self.assertTrue(MyContainer.__type__.global_allow)

    def test_tinfo_list_filtered(self):
        import ptahcms

        global MyContent, MyContainer
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptahcms.Container):
            __type__ = ptahcms.Type(
                'mycontainer', 'Container', filter_content_types=True)

        self.init_ptah()

        container = MyContainer()
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        MyContainer.__type__.allowed_content_types = ('mycontent',)
        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

    def test_tinfo_list_filtered_callable(self):
        import ptahcms

        global MyContent, MyContainer
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent', 'Content', permission=None)
        class MyContainer(ptahcms.Container):
            __type__ = ptahcms.Type(
                'mycontainer', 'Container', filter_content_types=True)

        self.init_ptah()

        container = MyContainer()
        self.assertEqual(MyContainer.__type__.list_types(container), [])

        def filter(content):
            return ('mycontent',)

        MyContainer.__type__.allowed_content_types = filter
        self.assertEqual(MyContainer.__type__.list_types(container),
                         [MyContent.__type__])

    def test_tinfo_conflicts(self):
        import ptahcms

        global MyContent
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent2', 'MyContent')
        class MyContent2(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent2', 'MyContent')

        self.assertRaises(ConfigurationConflictError, self.init_ptah)

    def test_tinfo_create(self):
        import ptahcms

        global MyContent
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent', 'MyContent')

        self.init_ptah()

        all_types = ptah.get_types()

        content = all_types['type:mycontent'].create(title='Test content')

        self.assertTrue(isinstance(content, MyContent))
        self.assertEqual(content.title, 'Test content')
        self.assertTrue(content not in ptah.get_session())

    def test_tinfo_alchemy(self):
        import ptahcms

        global MyContent
        class MyContent(ptahcms.Content):
            __tablename__ = "test_mycontents"
            __type__ = ptahcms.Type('mycontent', 'MyContent')

        self.init_ptah()

        self.assertEqual(
            MyContent.__mapper_args__['polymorphic_identity'], 'type:mycontent')

        self.assertTrue(
            MyContent.__uri_factory__().startswith('type-mycontent:'))

    def test_tinfo_resolver(self):
        import ptah, ptahcms

        global MyContent
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent2', 'MyContent')

        self.init_ptah()

        content = MyContent.__type__.create(title='Test content')
        c_uri = content.__uri__
        ptah.get_session().add(content)
        transaction.commit()

        c = ptah.resolve(c_uri)
        self.assertTrue(isinstance(c, MyContent))

    def test_tinfo_fieldset(self):
        import ptah, ptahcms

        MySchema = ptahcms.ContentSchema + \
            form.Fieldset(form.TextField('test'))

        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent2', 'MyContent',
                                     fieldset=MySchema)

        tinfo = MyContent.__type__
        self.assertIs(tinfo.fieldset, MySchema)

    def test_tinfo_fieldset_gen(self):
        import ptah, ptahcms

        global MyContent
        class MyContent(ptahcms.Content):
            __tablename__ = 'test_content'
            __type__ = ptahcms.Type('mycontent2', 'MyContent')

            test = sqla.Column(sqla.Unicode())

        self.init_ptah()

        tinfo = MyContent.__type__
        self.assertIn('test', tinfo.fieldset)
        self.assertIn('title', tinfo.fieldset)
        self.assertIn('description', tinfo.fieldset)
        self.assertNotIn('__owner__', tinfo.fieldset)
        self.assertEqual(len(tinfo.fieldset), 3)

    def test_tinfo_type_resolver(self):
        import ptah, ptahcms

        global MyContent
        class MyContent(ptahcms.Content):
            __type__ = ptahcms.Type('mycontent2', 'MyContent')

        self.init_ptah()

        tinfo_uri = MyContent.__type__.__uri__

        self.assertEqual(tinfo_uri, 'type:mycontent2')
        self.assertIs(ptah.resolve(tinfo_uri), MyContent.__type__)

    def test_names_filter(self):
        from ptahcms.tinfo import names_filter

        self.assertFalse(names_filter('_test'))
        self.assertFalse(names_filter('__test__'))
        self.assertTrue(names_filter('__test__', ('__test__',)))

        excludeNames = ('expires', 'contributors', 'creators',
                        'view', 'subjects',
                        'publisher', 'effective', 'created', 'modified')
        for name in excludeNames:
            self.assertFalse(names_filter(name))
            self.assertTrue(names_filter(name, (name,)))
