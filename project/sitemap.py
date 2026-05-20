from django.contrib.sitemaps import Sitemap

class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        return [
            '/',
            '/services/',
            '/calculator/',
            '/contacts/',
            '/privacy/',
        ]
    
    def location(self, item):
        return item

sitemaps = {
    'static': StaticSitemap,
}