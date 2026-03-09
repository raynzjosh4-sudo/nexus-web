import os
from django.core.management.base import BaseCommand
from storefront.client import get_supabase_client, get_supabase_service_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
BUCKET = "sitemaps"

def make_sitemap_xml(product_urls):
    from xml.etree.ElementTree import Element, SubElement, tostring
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in product_urls:
        url_elem = SubElement(urlset, "url")
        loc = SubElement(url_elem, "loc")
        loc.text = url
    return tostring(urlset, encoding="utf8", method="xml")

def make_index_xml(business_xml_urls):
    from xml.etree.ElementTree import Element, SubElement, tostring
    sitemapindex = Element("sitemapindex", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for sitemap_url in business_xml_urls:
        sitemap = SubElement(sitemapindex, "sitemap")
        loc = SubElement(sitemap, "loc")
        loc.text = sitemap_url
    return tostring(sitemapindex, encoding="utf8", method="xml")

class Command(BaseCommand):
    help = "Generates and uploads business and master sitemaps to Supabase storage."

    def handle(self, *args, **kwargs):
        supabase = get_supabase_client()
        service_client = get_supabase_service_client()

        # 1. One sitemap per ACTIVE business (filter: status='active')
        master_links = []
        businesses_response = supabase.table('business_profiles').select('*').eq('status', 'active').execute()
        businesses = businesses_response.data
        self.stdout.write(f"Found {len(businesses)} active businesses to process")

        for business in businesses:
            # Example: https://nexassearch.com/product/...
            posts_response = supabase.table('posts').select('id').eq('business_id', business['id']).execute()
            product_urls = [
                f"https://nexassearch.com/product/{post['id']}/"
                for post in posts_response.data
            ]
            if not product_urls:
                self.stdout.write(f"  ⚠️  Skipped: {business['business_name']} - No products")
                continue
            xml_bytes = make_sitemap_xml(product_urls)
            filename = f"business-{business['id']}.xml"
            try:
                service_client.storage.from_(BUCKET).remove([filename])
            except Exception:
                pass  # File doesn't exist yet, that's okay
            service_client.storage.from_(BUCKET).upload(filename, xml_bytes, {"content-type": "application/xml"})
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
            master_links.append(public_url)
            self.stdout.write(f"  ✅ {business['business_name']} ({business['domain']}) - {len(product_urls)} products")

        # 2. Master index
        self.stdout.write(f"Creating master index with {len(master_links)} sitemaps...")
        index_xml = make_index_xml(master_links)
        try:
            service_client.storage.from_(BUCKET).remove(["master_index.xml"])
        except Exception:
            pass  # File doesn't exist yet, that's okay
        service_client.storage.from_(BUCKET).upload(
            "master_index.xml", index_xml, {"content-type": "application/xml"}
        )
        self.stdout.write("✅ Uploaded master_index.xml")