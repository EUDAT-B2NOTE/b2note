import unittest
import requests
import json

LOCALHOST_ANNOTATIONS = 'http://localhost:5000/annotations'
LOCALHOST_APIDOCS = 'http://localhost:5000/api-docs'


class B2noteRestApiTestCase(unittest.TestCase):

    evethread = None  # type: None
    #check whether EVE server is accepting request by HEAD method, if not, start as separate thread
    @classmethod
    def setUpClass(self):
      self.headers = {
        'Content-Type': 'application/json',
      }
      # test whether eve server is up and running
      print('Setup ')
      try:
        response = self.head(self,'')
        print(response.status_code)
      except Exception as e:
        #print(e)
        print('Starting EVE server in separate thread ...')
        # code 200 is not returned, then start the eve server
        from b2note_api import app
        import multiprocessing
        import time
        self.evethread = multiprocessing.Process(target=app.run)
        self.evethread.start()
        time.sleep(2)
        print('Started EVE server ...')


    #if server was started as separate thread, then terminate it after all tests
    @classmethod
    def tearDownClass(self):
      self.headers = {}

      # if the eve was started - then it will be stopped when the test process will terminate
      if self.evethread:
        self.evethread.terminate()
        print('Stopped EVE server ...')


    def head(self,resource):
      return requests.head(LOCALHOST_ANNOTATIONS+'/'+resource,headers=self.headers)

    def get(self,resource):
      return requests.get(LOCALHOST_ANNOTATIONS + '/' + resource, headers=self.headers)

    def delete(self,resource,etag):
      return requests.delete(LOCALHOST_ANNOTATIONS+'/'+resource,headers={'Content-Type':'application/json','Authorization': 'Basic dGVzdDp0ZXN0','If-Match':etag})

    def get(self,resource):
      return requests.get(LOCALHOST_ANNOTATIONS + '/' + resource, headers=self.headers)

    def getapidocs(self,resource=""):
      return requests.get(LOCALHOST_APIDOCS + '/' + resource, headers=self.headers)

    def post(self,data):
      return requests.post(LOCALHOST_ANNOTATIONS, headers={'Content-Type':'application/json','Authorization': 'Basic dGVzdDp0ZXN0'}, data=data)

    def test_getAnnotation(self):
      response = self.get('')
      self.assertIn(b'"_meta":', response.content)

    def test_create_annotation(self):
      data = '{"id":"http://example.org/anno1","body":"http://example.com/post1","target":"http://example.com/page1"}'
      response = self.post(data)
      #print(response.content)
      assert b'"_status": "OK"' in response.content

    def test_create_annotation_bodyValue(self):
      data = '{"id":"http://example.org/anno1","bodyValue":"Comment here","target":"http://example.com/page1"}'
      response = self.post(data)
      #print(response.content)
      assert b'"_status": "OK"' in response.content


    def test_missing_target(self):
      data = '{"id":"1","body":"tests11.5"}'
      response = self.post(data)
      #print(response.content)
      assert b'Insertion failure' in response.content

    def test_bad_body_as_integer(self):
      data = '{"id":"1","body":3}'
      response = self.post(data)
      #print(response.content)
      assert b'Insertion failure' in response.content

    def test_create_annotation_get_annotation_detail(self):
      data = '{"id":"http://example.org/anno1","body":"http://example.com/post1","target":"http://example.com/page1"}'
      response = self.post(data)
      #print(response.content)
      responsedata = json.loads(response.content)
      #print(responsedata)
      assert b'"_status": "OK"' in response.content
      #print(response.content)
      self.assertIsInstance(responsedata['_id'], str)
      response2 = self.get(responsedata['_id'])
      responsedata2 = json.loads(response2.content)
      #print(responsedata2)
      self.assertEqual(responsedata['_id'],responsedata2['_id'])

    def test_stringbody_schema(self):
      body = '{"id":"http://example.org/anno1","body":"http://example.com/post1","target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)

    def test_listbody_schema(self):
      body = '{"id":"http://example.org/anno1","body":["http://example.com/post1","http://example.com/post2"],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)

    def test_listbodyids_schema(self):
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1"},{"id":"http://example.com/post2"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)

    def test_listbodyformat_language_processinglanguage_textdirection_schema(self):
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1","format":"audio/mpeg"},{"id":"http://example.com/post2","format":"application/pdf"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1","format":["audio/mpeg","audio/mp3"]},{"id":"http://example.com/post2","format":"application/pdf"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1","format":"audio/mpeg","language":"en"},{"id":"http://example.com/post2","format":"application/pdf"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1","format":"audio/mpeg","language":"en","processingLanguage":"en-UK"},{"id":"http://example.com/post2","format":"application/pdf"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1","format":"audio/mpeg","language":"en","processingLanguage":"en-UK","textDirection":"auto"},{"id":"http://example.com/post2","format":"application/pdf"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":[{"id":"http://example.com/post1","format":"audio/mpeg","language":"en","processingLanguage":"en-UK","textDirection":"badvalue"},{"id":"http://example.com/post2","format":"application/pdf"}],"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertNotIn(b'"_status": "OK"',response.content)

    def test_structbody(self):
      body = '{"id":"http://example.org/anno1","body":{"id":"http://example.com/post1","type":"Text"},"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":{"id":"http://example.com/post1","type":"BadValue"},"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'unallowed value BadValue',response.content)
      body = '{"id":"http://example.org/anno1","body":{"id":"http://example.com/post1","type":"TextualBody","value":"TestValue"},"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":{"id":"http://example.com/post1","type":"Choice","items":["TestValue","TestValue2"]},"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'"_status": "OK"',response.content)
      body = '{"id":"http://example.org/anno1","body":{"id":"http://example.com/post1","type":"Choice","items":"BadTestValueShouldBeList"},"target":"http://example.com/page1"}'
      response = self.post(body)
      #print(response.content)
      self.assertIn(b'must be of list type',response.content)
      #self.assertIn(b'"_status": "OK"' in response.content

    def test_annotationfromui(self):
      body ='{"@context":"http://www.w3/org/ns/anno/jsonld","id":"","type":"Annotation","body":{"type":"SpecificResource","source":"protein"},"target":{"id":"http://hdl.handle.net/11304/3e69a758-dbea-46cb-b9a1-2b2974531c19","type":"SpecificResource","source":"https://b2share.eudat.eu/api/files/b381828e-59de-4323-b636-7600a6b04bf2/acqu3s"},"motivation":"tagging","creator":{"type":"Person","nickname":"Guest"},"generator":{"type":"Software","homepage":{"href":"http://localhost/b2note/#/","origin":"http://localhost","protocol":"http:","host":"localhost","hostname":"localhost","port":"","pathname":"/b2note/","search":"","hash":"#/"},"name":"B2Note v2.0"},"created":"2019-06-12T11:01:25.654Z","generated":"2019-06-12T11:01:25.654Z"}'
      response = self.post(body)
      self.assertIn(b'"_status": "OK"',response.content)

    def test_deleteannotations(self):
      response = self.get("")
      data = json.loads(response.content)
      for item in data["_items"]:
        #print('deleting item',item["_id"])
        response2 = self.delete(item["_id"],item["_etag"])
        self.assertIn(b'',response2.content)

    # def test_deleteallannotations(self):
    #   deleteannotations = True
    #   # delete all annotations
    #   while deleteannotations:
    #     response = self.get('')
    #     data = json.loads(response.content)
    #     deleteannotations = len(data["_items"])>0
    #     for item in data["_items"]:
    #       self.delete( item["_id"],item["_etag"])



    def test_apidocs(self):

      response=self.getapidocs()
      self.assertIn(b"\"swagger\":\"2.0\"",response.content)

if __name__ == '__main__':
    unittest.main()



