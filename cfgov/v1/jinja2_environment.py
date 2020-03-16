import os.path

from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.defaultfilters import linebreaksbr, pluralize, slugify
from django.utils.translation import ugettext, ungettext

from jinja2 import Environment


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class RelativeTemplatePathEnvironment(Environment):
    """Jinja2 environment that supports template loading with relative paths.

    By default, Jinja2 (and Django) template loading works with "absolute"
    paths relative to the root template directories specified in Django
    settings. Consider, for example, if the root template directories include
    a directory like /foo, and within that directory there exists some
    template /foo/bar/template.html, and that template includes this
    directive:

    {% include "other_template.html" %}

    by default, the template loader will look to load that template relative
    to the root template directories. In this case, it would look to load
    the template /foo/other_template.html.

    This custom Jinja2 environment class modifies that behavior to also
    support relative template loading, which would make the search path look
    like this instead:

    /foo/bar/other_template.html
    /foo/other_template.html

    This logic adds relative paths to the template search tree, that take
    precendence over the default loader source directories.
    """
    def join_path(self, template, parent):
        dirname = os.path.dirname(parent)
        segments = dirname.split('/')
        paths = []
        collected = ''
        for segment in segments:
            collected += segment + '/'
            paths.insert(0, collected[:])
        for p in paths:
            relativepath = os.path.join(p, template)
            for search in self.loader.searchpath:
                filesystem_path = os.path.join(search, relativepath)
                if os.path.exists(filesystem_path):
                    return relativepath
        return template


class JinjaTranslations(object):
    def ugettext(self, message):
        return ugettext(message)

    def ungettext(self, singular, plural, number):
        return ungettext(singular, plural, number)


def environment(**options):
    env = RelativeTemplatePathEnvironment(**options)
    env.autoescape = True

    # Requires the jinja2.ext.i18n extension.
    env.install_gettext_translations(JinjaTranslations(), newstyle=True)

    # Expose various Django methods into the Jinja2 environment.
    env.globals.update({
        'get_messages': messages.get_messages,
        'reverse': reverse,
        'static': staticfiles_storage.url,
        'url': reverse,
    })

    env.filters.update({
        'linebreaksbr': linebreaksbr,
        'pluralize': pluralize,
        'slugify': slugify,
    })

    return env
