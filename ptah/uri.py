""" uri resolver """
import uuid
from memphis import config

resolvers = {}
resolversInfo = {}


def resolve(uri):
    if not uri:
        return

    try:
        type, uuid = uri.split(':', 1)
    except ValueError:
        return None

    try:
        return resolvers[type](uri)
    except KeyError:
        pass

    return None


def extractUriType(uri):
    if uri:
        try:
            type, uuid = uri.split(':', 1)
            return type
        except:
            pass

    return None


def registerResolver(type, component, title='', description='', depth=1):
    resolvers[type] = component
    resolversInfo[type] = (title, description)

    info = config.DirectiveInfo(depth=depth)
    info.attach(
        config.Action(None, discriminator = ('ptah:uri-resolver',type))
        )


class UUIDGenerator(object):

    def __init__(self, type):
        self.type = type

    def __call__(self):
        return '%s:%s'%(self.type, uuid.uuid4().get_hex())
