import unittest
from unittest.mock import patch
from app.services.factcheck import extract_claims
from app.services.providers import ProviderError, source_type

class LogicTests(unittest.TestCase):
    def test_instruction_filter_and_duplicate_filter(self):
        response={"claims":[
          {"claim":"Revenue reached $12 million in 2025.","excerpt":"Revenue $12m","page":1,"claim_type":"financial"},
          {"claim":"Revenue reached $12 million in 2025.","excerpt":"Revenue $12m","page":1,"claim_type":"financial"},
          {"claim":"The application must provide a dashboard.","excerpt":"must provide","page":1,"claim_type":"other"}]}
        with patch("app.services.factcheck.groq_json",return_value=response):
            claims,excluded=extract_claims([{"page":1,"text":"demo"}],"key","model",5)
        self.assertEqual(len(claims),1); self.assertEqual(excluded,2)
    def test_source_classification(self):
        self.assertEqual(source_type("https://www.nasa.gov/x"),"Government")
        self.assertEqual(source_type("https://www.example.com/x"),"Other — review source")
    def test_provider_error(self):
        e=ProviderError("Groq","rate limit",429)
        self.assertEqual(e.status_code,429); self.assertEqual(e.provider,"Groq")

if __name__=="__main__": unittest.main()
