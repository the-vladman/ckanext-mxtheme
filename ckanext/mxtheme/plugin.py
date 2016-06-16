import datetime
import logging
import urlparse
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.helpers import _add_i18n_to_url
from pylons import config
from routes import url_for as _routes_default_url_for


def format_display_date(time_stamp, format_date="%Y/%m/%d"):
    date_object = datetime.datetime.strptime(time_stamp, "%Y-%m-%dT%H:%M:%S.%f")
    return date_object.strftime(format_date)

def is_regular_format(format):
    return True if format in ['csv', 'xml', 'shp', 'kml', 'kmz', 'json', 'xls', 'txt', 'tls'] else False

def get_site_protocol_and_host():
    '''Return the protocol and host of the configured `ckan.site_url`.
    This is needed to generate valid, full-qualified URLs.
    If `ckan.site_url` is set like this::
        ckan.site_url = http://example.com
    Then this function would return a tuple `('http', 'example.com')`
    If the setting is missing, `(None, None)` is returned instead.
    '''
    site_url = config.get('ckan.site_url', None)
    logging.info('ckan.site_url {0}'.format(site_url))
    if site_url is not None:
        parsed_url = urlparse.urlparse(site_url)
        return (
            parsed_url.scheme.encode('utf-8'),
            parsed_url.netloc.encode('utf-8')
        )
    return (None, None)

def url_for(*args, **kw):
    '''Return the URL for the given controller, action, id, etc.
    Usage::
        import ckan.plugins.toolkit as toolkit
        url = toolkit.url_for(controller='package', action='read',
                              id='my_dataset')
        => returns '/dataset/my_dataset'
    Or, using a named route::
        toolkit.url_for('dataset_read', id='changed')
    This is a wrapper for :py:func:`routes.url_for` that adds some extra
    features that CKAN needs.
    '''
    locale = kw.pop('locale', None)
    # remove __ckan_no_root and add after to not pollute url
    no_root = kw.pop('__ckan_no_root', False)
    # routes will get the wrong url for APIs if the ver is not provided
    if kw.get('controller') == 'api':
        ver = kw.get('ver')
        if not ver:
            raise Exception('api calls must specify the version! e.g. ver=3')
        # fix ver to include the slash
        kw['ver'] = '/%s' % ver
    if kw.get('qualified', False):
        kw['protocol'], kw['host'] = get_site_protocol_and_host()
    my_url = _routes_default_url_for(*args, **kw)
    kw['__ckan_no_root'] = no_root
    return _add_i18n_to_url(my_url, locale=locale, **kw)


class MxthemePlugin(plugins.SingletonPlugin):
    # IConfigurer
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'mxtheme')

    def get_helpers(self):
        return {'format_display_date': format_display_date, 'is_regular_format': is_regular_format, 'url_for': url_for}