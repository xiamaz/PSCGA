import requests
from pprint import pprint

class OmimSession(requests.Session):
    host = 'http://api.omim.org/api/{}'
    def __init__(self, api_key):
        super().__init__()
        self.headers['ApiKey'] = api_key

    def retrieve_references(self, omim_id):
        params = {
                'mimNumber' : omim_id
                ,'include' : 'referenceList'
                ,'format' : 'json'
                }
        r = self.get(self.host.format('entry'), params=params)
        r.raise_for_status()
        entries = r.json()['omim']['entryList']
        assert len(entries) == 1
        e = entries[0]['entry']
        return e['referenceList']

class PubmedSession(requests.Session):
    def __init__(self):
        super().__init__()
        self.params['tool'] = 'PSCGA'
        self.params['email'] = 'alcasa.mz@gmail.com'
        self.params['retmode'] = 'json'

    def search(self, term):
        retstart = 0
        retmax = 1000
        id_list = []
        while True:
            param = { 'db' : 'pubmed'
                ,'term' : term
                ,'retstart' : retstart
                ,'retmax' : retmax
                }
            r = self.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi', params=dict(self.params, **param)).json()
            count = int(r['esearchresult']['count'])
            retstart = int(r['esearchresult']['retstart'])
            retmax = int(r['esearchresult']['retmax'])
            id_list += r['esearchresult']['idlist']
            if retmax + retstart >= count:
                break
            retstart += retmax
        return id_list

    def cited_by(self, pubmedid):
        param = {'dbfrom' : 'pubmed'
                ,'linkname' : 'pubmed_pubmed_citedin'
                ,'id' : pubmedid}
        r = self.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi',params=dict(self.params, **param))
        print(r.text)
        return r

    def cites_from(self, pubmedid):
        param = {'dbfrom' : 'pubmed'
                ,'linkname' : 'pubmed_pubmed_refs'
                ,'id' : pubmedid}
        r = self.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi',params=dict(self.params, **param))
        print(r.text)
        return r

def ref_stat(omim_refs):
    num_refs = len(omim_refs)
    pubmed = 0
    doi = 0
    for entry in omim_refs:
        ref = entry['reference']
        if 'pubmedID' in ref:
            pubmed += 1
        if 'doi' in ref:
            doi += 1

    print("DOI: {}/{}".format(doi, num_refs))
    print("Pubmed: {}/{}".format(pubmed, num_refs))

def main():
    omim_key = open('omim.key', 'r').read().strip()
    os = OmimSession(omim_key)
    r = os.retrieve_references("161200")
    ref_stat(r)
    ps = PubmedSession()
    ps.search('nicolaides baraitser')

if __name__ == '__main__':
    main()
