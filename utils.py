
import concurrent.futures
from requests import get as requests_get

class Utils(object):

    @classmethod
    def load_url(cls, url='', timeout=5):
            r = requests_get(url, timeout=timeout)
            # consider using defuse here and not "later" in parsing xml files..
            return r.content

    @classmethod
    def async_crawl(cls, urls_list=[], timeout=60):
        # https://www.python.org/dev/peps/pep-3148/#web-crawl-example
        # https://docs.python.org/3.8/library/concurrent.futures.html#threadpoolexecutor-example
        # import asyncio    # this library may be better the python standart concurrency module.
        print('Crawling {} urls...'.format(len(urls_list)))

        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {executor.submit(cls.load_url, url, timeout): url for url in urls_list}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url, exc))
                else:
                    pass
                    print('%r page is %d bytes' % (url, len(data)))
        print('... Done.\n')
        return future_to_url



