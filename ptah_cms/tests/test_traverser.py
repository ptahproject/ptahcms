import ptah
import transaction
from memphis import config
from pyramid.interfaces import ITraverser

from base import Base


class TestTraverser(Base):

    def tearDown(self):
        config.cleanUp(self.__class__.__module__)
        super(TestTraverser, self).tearDown()

    def _create_content(self):
        import ptah_cms

        for c in ptah_cms.Session.query(ptah_cms.Content).all():
            ptah_cms.Session.delete(c)
        transaction.commit()

        factory = ptah_cms.ApplicationFactory('/test', 'root', 'Root App')
        self.factory = factory

        class MyContent(ptah_cms.Content):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('test')

        root = factory()

        folder = MyContent(
            __name__ = 'folder',
            __parent__ = root,
            __path__ = '%sfolder/'%root.__path__)
        self.folder_uri = folder.__uri__

        content = MyContent(
            __name__ = 'content',
            __parent__ = folder,
            __path__ = '%scontent/'%folder.__path__)
        self.content_uri = content.__uri__

        ptah_cms.Session.add(folder)
        ptah_cms.Session.add(content)
        transaction.commit()

    def test_traverser_root_view(self):
        import ptah_cms
        from ptah_cms.traverser import ContentTraverser

        self._create_content()

        request = self._makeRequest(
            {'PATH_INFO': '/test/index.html'})

        root = self.factory(request)

        traverser = ITraverser(root)

        self.assertTrue(isinstance(traverser, ContentTraverser))

        info = traverser(request)
        self.assertTrue(info['context'] is root)
        self.assertEqual(info['view_name'], 'index.html')

    def test_traverser_root_no_view(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertTrue(info['context'] is root)
        self.assertEqual(info['view_name'], '')

    def test_traverser_folder(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.folder_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder',))

    def test_traverser_folder_2(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.folder_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder',))

    def test_traverser_folder_view(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/index.html'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.folder_uri)
        self.assertEqual(info['view_name'], 'index.html')
        self.assertEqual(info['traversed'], ('folder',))

    def test_traverser_folder_subcontent1(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/content'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder','content'))

    def test_traverser_folder_subcontent2(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest({'PATH_INFO': '/test/folder/content/'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], '')
        self.assertEqual(info['traversed'], ('folder','content'))

    def test_traverser_folder_subcontent_view(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest(
            {'PATH_INFO': '/test/folder/content/index.html'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], 'index.html')
        self.assertEqual(info['traversed'], ('folder','content'))

    def test_traverser_folder_subcontent_view2(self):
        import ptah_cms
        self._create_content()

        request = self._makeRequest(
            {'PATH_INFO': '/test//folder//content/index.html'})

        root = self.factory(request)
        traverser = ITraverser(root)

        info = traverser(request)
        self.assertEqual(info['context'].__uri__, self.content_uri)
        self.assertEqual(info['view_name'], 'index.html')
        self.assertEqual(info['traversed'], ('folder','content'))