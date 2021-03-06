import unittest
#https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb
"""It works"""
from pymongo import MongoClient
from random import randint
import gridfs
from import_help import modINFO74000
import modINFO74000.misc_func as misc
from modINFO74000.misc_func import PATH_TO_JSON_FILES
from modINFO74000.misc_func import PATH_TO_IMAGE_FILES


def setUpModule():
        print("----- PyMongo data representation unitest Suite begins")
def tearDownModule():        
        print("\n----- PyMongo data representation unitest Suite ends")



#@unittest.skip("")
class TestClass1_pymongo_business_review(unittest.TestCase):
        client=None
        db=None
        
        @classmethod
        def CreateFakeBusinessReviews(cls):
                #https://www.mongodb.com/blog/post/getting-started-with-python-and-mongodb
                names = ['Kitchen','Animal','State', 'Tastey', 'Big','City','Fish', 'Pizza','Goat', 'Salty','Sandwich','Lazy', 'Fun']
                company_type = ['LLC','Inc','Company','Corporation']
                company_cuisine = ['Pizza', 'Bar Food', 'Fast Food', 'Italian', 'Mexican', 'American', 'Sushi Bar', 'Vegetarian']
                for x in range(1, 501):
                        business = {
                                'name' : names[randint(0, (len(names)-1))] + ' ' + names[randint(0, (len(names)-1))]  + ' ' + company_type[randint(0, (len(company_type)-1))],
                                'rating' : randint(1, 5),
                                'cuisine' : company_cuisine[randint(0, (len(company_cuisine)-1))] 
                        }
                        #Step 3: Insert business object directly into MongoDB via insert_one
                        result=cls.db.reviews.insert_one(business)
                        #Step 4: Print to the console the ObjectID of the new document
                        print('Created {0} of 500 as {1}'.format(x,result.inserted_id))
                print('finished creating 500 fake business reviews')


        @classmethod
        def setUpClass(cls):
                #Step 1: Connect to MongoDB - Note: Change connection string as needed
                cls.client = MongoClient("mongodb://127.0.0.1:27017")
                cls.db=cls.client.testdb

                #Step 2: Create sample data, but only if collection does not exist   
                if cls.db.reviews.find_one()==None: 
                        print("Fake reviews collection does NOT exist. It will be created")
                        cls.CreateFakeBusinessReviews()
                else: print("Fake reviews collection already exists.")

        @classmethod
        def tearDownClass(cls):
                #Step 5: clear database object
                cls.client.close()
                cls.db=None        

        def test_case01(self):
                print("Fake review collection found in database")
                collection_cursor=self.db.list_collections(filter={'name':'reviews'})
                if collection_cursor==None:
                         self.fail("cannot find the fake reviews collection")
                else:
                        print(collection_cursor.next())
                
        #@unittest.skip("avoid listing records")
        def test_case03(self):
                reviews = self.db.reviews.find({'cuisine':'Italian'})
                for doc in reviews: 
                        print(doc)                                 

        #@unittest.skip("avoid listing records")
        def test_case04(self):
                reviews = self.db.reviews.find({'rating':'5'})
                for doc in reviews: 
                        print(doc)                                 

        def test_case05(self):
                pizza_lazy_review = self.db.reviews.find_one({'name': 'Pizza Lazy LLC'})
                if pizza_lazy_review!=None: print("Found one Pizza Lazy review:",pizza_lazy_review)
                else: print("Could not find a review for Pizza Lazy LLC")
                
                goat_city_review = self.db.reviews.find_one({'name': 'Goat City LLC'})
                if goat_city_review!=None: print("Found one Goat City review:",goat_city_review)
                else: print("Could not find a review for Goat City LLC")
                        
#@unittest.skip("")
class TestClass2_pymongo_gridfs(unittest.TestCase):
        client=None
        db=None

        @classmethod
        def setUpClass(cls):
                cls.client=MongoClient(port=27017)
                cls.db=cls.client.testdb

        @classmethod
        def tearDownClass(cls):
                cls.client.close()
                cls.db=None

        def test_case01(self):
                # Issue the serverStatus command and print the results
                serverStatusResult=self.db.command("serverStatus")
                #print(serverStatusResult)
                #self.assertEqual(float(serverStatusResult['OK']),1.0,"MongoDB Server status Error")

        def test_case02(self):
                record_collection = self.db.records
                if record_collection.find_one({'author':'S Pantazi'})==None:
                        record_data = {
                                'title': 'This is a document',
                                'subject': 'This is a test record',
                                'author': 'S Pantazi',
                                'data':"test data"
                        }
                        result = record_collection.insert_one(record_data)
                        print('One record inserted: {0}'.format(result.inserted_id))

       #@unittest.skip("")
        def test_case03_list_gridfs_files(self):
                print("GridFS files")
                fs = gridfs.GridFS(self.db)
                for f in list(fs.find()):
                        print("id:{0}, file name:{1}, content:{2}, len:{3}, upload date:{4}".format(
                                f._id,
                                f.filename,
                                f.content_type,
                                f.length,
                                f.upload_date
                                ))

        TEST_BINARY_FILE_NAME="GHouse.png"

        #binary gridfs files
        def test_case04_write_binary_file_to_gridfs(self):
                print("Put/Write/Upload GridFS file: ",self.TEST_BINARY_FILE_NAME)     
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.TEST_BINARY_FILE_NAME): 
                        print("File exists: ",self.TEST_BINARY_FILE_NAME)
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.TEST_BINARY_FILE_NAME,"br")                          
                        #fs.put(f,filename=self.TEST_BINARY_FILE_NAME)
                        with fs.new_file(filename=self.TEST_BINARY_FILE_NAME,foo="baz") as img: 
                                img.write(f)
                                img.close()           
                        f.close()

        def test_case05_read_binary_file_from_gridfs(self):
                print("Get/Read/Download last version of a GridFS file")                
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.TEST_BINARY_FILE_NAME) as img:
                        print('Found file for.',img._id)  
                        f=open(PATH_TO_IMAGE_FILES+"/GHouse_copy.png",'bw')
                        data=img.read()
                        f.write(data)         
                        f.close()  
                        img.close()
                        self.assertGreater(img.length,0,"GridFS binary file has zero length. Something is wrong.")
                

#@unittest.skip("")
class TestClass3_pymongo_healthcare_MiniEMR(unittest.TestCase):
        client=None
        db=None

        @classmethod
        def setUpClass(cls):
                cls.client=MongoClient(port=27017)
                cls.db=cls.client.mini_emr

        @classmethod
        def tearDownClass(cls):
                cls.client.close()
                cls.db=None

        def test_case02_labs(self):
                lab_collection = self.db.labs
                if lab_collection.find_one({})==None:
                        labListObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/Loinc_covid.json")
                        insert_result = lab_collection.insert_many(labListObj)
                        print('Lab records inserted: ',insert_result.inserted_ids)

        def test_case02_patients(self):
                patient_collection = self.db.patients
                if patient_collection.find_one({})==None:
                        patientListObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/patients.json")
                        insert_result = patient_collection.insert_many(patientListObj)
                        print('Patient records inserted: ',insert_result.inserted_ids)

        def test_case03_employees(self):
                employee_collection = self.db.employees
                if employee_collection.find_one({})==None:
                        employeeListObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/empl.json")
                        insert_result = employee_collection.insert_many(employeeListObj)
                        print('Employee records inserted: ',insert_result.inserted_ids)

        def test_case06_drug_formulary(self):
                formulary_collection = self.db.drug_formulary
                if formulary_collection.find_one({})==None:
                        drugDataObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/drug_data.json")
                        insert_result = formulary_collection.insert_many(drugDataObj["DrugReport"])
                        print('Drug records inserted: ',insert_result.inserted_ids)

        def test_case04_employee_search(self):
                EMPLOYEE_QUERY={'full_name': {'$regex' : "^WILSON"}} #use regex for query
                employee_collection = self.db.employees
                query_result=employee_collection.find_one(EMPLOYEE_QUERY)
                if query_result!=None:
                        print('Employee found: ',query_result)
                else: self.fail("Could not find Dr. WILSON")

        def test_case05_employee_search_dr_house(self):
                EMPLOYEE_QUERY={'full_name': {'$regex' : "^HOUSE"}} #use regex for query
                employee_collection = self.db.employees
                query_result=employee_collection.find_one(EMPLOYEE_QUERY)
                if query_result!=None:
                        print('Employee found: ',query_result)
                else: self.fail("Could not find Dr. HOUSE")         

        def test_case05_5_patient_list(self):
                query_result=self.db.patients.find()
                if query_result!=None:
                        print('Patients found: ',query_result)
                        for p in query_result: 
                                print(p)    
                else: self.fail("Could not find any patients")         
                      

        def test_case06_drug_formulary(self):
                formulary_collection = self.db.drug_formulary
                if formulary_collection.find_one({})==None:
                        drugDataObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/drug_data.json")
                        insert_result = formulary_collection.insert_many(drugDataObj["DrugReport"])
                        print('Drug records inserted: ',insert_result.inserted_ids)
                                        

        def test_case07_drug_search(self):
                DRUG_QUERY={'TRADENAME': {'$regex' : "^PAROXETINE"}} #use regex for query
                formulary_collection = self.db.drug_formulary
                query_result=list(formulary_collection.find(DRUG_QUERY))
                self.assertEqual(len(query_result),22,"There are 22 records that start with the name Paroxetine in the drug database")

        GHOUSE_PHOTO_FILE_NAME='GHouse.png'
        BTEST_PHOTO_FILE_NAME='bob_test.png'
        ATEST_PHOTO_FILE_NAME='Anne-Wallace.png'
        RTEST_PHOTO_FILE_NAME='GracyOMalley.png'
        TTURNER_PHOTO_FILE_NAME='Fred-Viidul.png'
        CHILL_PHOTO_FILE_NAME='MyHeadPic.png'
        PHIL_PHOTO_FILE_NAME='Steve-Schmidt.png'
        CASEY_PHOTO_FILE_NAME='Lene-Aaling.png'

        def test_case08_ghouse_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.GHOUSE_PHOTO_FILE_NAME): 
                        print("Ghouse image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.GHOUSE_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.GHOUSE_PHOTO_FILE_NAME,tag="INFO74000") as img: 
                                img.write(f)
                                img.close()           
                        f.close()
     
        def test_case08_atest_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.ATEST_PHOTO_FILE_NAME): 
                        print("Alice Test image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.ATEST_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.ATEST_PHOTO_FILE_NAME,tag="INFO74000") as img: 
                                img.write(f)
                                img.close()           
                        f.close()
        
        def test_case08_rtest_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.RTEST_PHOTO_FILE_NAME): 
                        print("Rob Test image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.RTEST_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.RTEST_PHOTO_FILE_NAME,tag="INFO74000") as img: 
                                img.write(f)
                                img.close()           
                        f.close()

        def test_case09_btest_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.BTEST_PHOTO_FILE_NAME): 
                        print("Bob Test image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.BTEST_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.BTEST_PHOTO_FILE_NAME,tag="Test,Bob") as img: 
                                img.write(f)
                                img.close()           
                        f.close()

        def test_case09_phil_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.PHIL_PHOTO_FILE_NAME): 
                        print("Phil image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.PHIL_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.PHIL_PHOTO_FILE_NAME,tag="MacLellan,Phil") as img: 
                                img.write(f)
                                img.close()           
                        f.close()

        def test_case09_casey_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.CASEY_PHOTO_FILE_NAME): 
                        print("Casey image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.CASEY_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.CASEY_PHOTO_FILE_NAME,tag="Jones,Casey") as img: 
                                img.write(f)
                                img.close()           
                        f.close()                        

        def test_case09_chill_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.CHILL_PHOTO_FILE_NAME): 
                        print("Christian Hill image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.CHILL_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.CHILL_PHOTO_FILE_NAME,tag="Hill,Christian") as img: 
                                img.write(f)
                                img.close()           
                        f.close()

        def test_case09_tturner_upload_photo(self):
                fs = gridfs.GridFS(self.db)
                if fs.exists(filename=self.TTURNER_PHOTO_FILE_NAME): 
                        print("Timmy Turner image file exists")
                else:
                        f=open(PATH_TO_IMAGE_FILES+"/"+self.TTURNER_PHOTO_FILE_NAME,"br") 
                        with fs.new_file(filename=self.TTURNER_PHOTO_FILE_NAME,tag="Turner,Timmy") as img: 
                                img.write(f)
                                img.close()           
                        f.close()                       

        def test_case10_ghouse_update_record_with_photo(self):
                '''update Dr. House record with the photo, and login credentials'''
                GHOUSE_USERNAME='ghouse'
                GHOUSE_PASSWORD='abc123'
                EMPLOYEE_QUERY={'full_name': {'$regex' : "^HOUSE"}} #use regex for query
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.GHOUSE_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        employee_collection = self.db.employees
                        ghouse_record_query_result=employee_collection.find_one(EMPLOYEE_QUERY)
                        if ghouse_record_query_result==None:
                                self.fail("Could not find Dr. HOUSE's record")                
                        else:                                 
                                print('GHouse record found: ',ghouse_record_query_result)
                                #check if record has the photo field; if not, add it
                                employee_collection.update_one(
                                        {'_id':ghouse_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id,'username':GHOUSE_USERNAME,'password':GHOUSE_PASSWORD}})
                        img.close()

        def test_case10_chill_update_record_with_photo(self):
                '''update Dr. Hill record with the photo, and login credentials'''
                CHILL_USERNAME='chill'
                CHILL_PASSWORD='Abc123'
                EMPLOYEE_QUERY={'full_name': {'$regex' : "^HILL"}} #use regex for query
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.CHILL_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        employee_collection = self.db.employees
                        chill_record_query_result=employee_collection.find_one(EMPLOYEE_QUERY)
                        if chill_record_query_result==None:
                                self.fail("Could not find Dr. Hill's record")                
                        else:                                 
                                print('CHill record found: ',chill_record_query_result)
                                #check if record has the photo field; if not, add it
                                employee_collection.update_one(
                                        {'_id':chill_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id,'username':CHILL_USERNAME,'password':CHILL_PASSWORD}})
                        img.close()

        def test_case10_tturner_update_record_with_photo(self):
                '''update Dr. Turner record with the photo, and login credentials'''
                TTURNER_USERNAME='tturner'
                TTURNER_PASSWORD='abc123'
                EMPLOYEE_QUERY={'full_name': {'$regex' : "^TURNER"}} #use regex for query
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.TTURNER_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        employee_collection = self.db.employees
                        tturner_record_query_result=employee_collection.find_one(EMPLOYEE_QUERY)
                        if tturner_record_query_result==None:
                                self.fail("Could not find Dr. Turner's record")                
                        else:                                 
                                print('TTurner record found: ',tturner_record_query_result)
                                #check if record has the photo field; if not, add it
                                employee_collection.update_one(
                                        {'_id':tturner_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id,'username':TTURNER_USERNAME,'password':TTURNER_PASSWORD}})
                        img.close()

        def test_case11_bob_test_update_record_with_photo(self):
                '''update Bob Test patient record with the photo'''
                BTEST_PATIENT_QUERY={'id': 12346} 
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.BTEST_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        patient_collection = self.db.patients
                        btest_record_query_result=patient_collection.find_one(BTEST_PATIENT_QUERY)
                        if btest_record_query_result==None:
                                self.fail("Could not find Bob Test's record")                
                        else:                                 
                                print('Bob Test record found: ',btest_record_query_result)
                                #check if record has the photo field; if not, add it
                                patient_collection.update_one(
                                        {'_id':btest_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id}})
                        img.close()

        def test_case11_rob_test_update_record_with_photo(self):
                '''update Rob Test patient record with the photo'''
                RTEST_PATIENT_QUERY={'id': 12345} 
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.RTEST_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        patient_collection = self.db.patients
                        rtest_record_query_result=patient_collection.find_one(RTEST_PATIENT_QUERY)
                        if rtest_record_query_result==None:
                                self.fail("Could not find Rob Test's record")                
                        else:                                 
                                print('Rob Test record found: ',rtest_record_query_result)
                                #check if record has the photo field; if not, add it
                                patient_collection.update_one(
                                        {'_id':rtest_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id}})
                        img.close()

        def test_case11_alice_test_update_record_with_photo(self):
                '''update Alice Test patient record with the photo'''
                ATEST_PATIENT_QUERY={'id': 1234} 
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.ATEST_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        patient_collection = self.db.patients
                        atest_record_query_result=patient_collection.find_one(ATEST_PATIENT_QUERY)
                        if atest_record_query_result==None:
                                self.fail("Could not find Alice Test's record")                
                        else:                                 
                                print('Alice Test record found: ',atest_record_query_result)
                                #check if record has the photo field; if not, add it
                                patient_collection.update_one(
                                        {'_id':atest_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id}})
                        img.close()

        def test_case11_phil_update_record_with_photo(self):
                '''update phil patient record with the photo'''
                PHIL_PATIENT_QUERY={'id': 12347} 
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.PHIL_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        patient_collection = self.db.patients
                        phil_record_query_result=patient_collection.find_one(PHIL_PATIENT_QUERY)
                        if phil_record_query_result==None:
                                self.fail("Could not find PHIL's record")                
                        else:                                 
                                print('Phil record found: ',phil_record_query_result)
                                #check if record has the photo field; if not, add it
                                patient_collection.update_one(
                                        {'_id':phil_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id}})
                        img.close()

        def test_case11_casey_update_record_with_photo(self):
                '''update casey patient record with the photo'''
                CASEY_PATIENT_QUERY={'id': 12348} 
                fs = gridfs.GridFS(self.db)
                with fs.get_last_version(self.CASEY_PHOTO_FILE_NAME) as img:
                        print('Found image file with id: ',img._id)  
                        self.assertGreater(img.length,0,"Image file has zero length. Something is wrong.")
                        #image is OK, now update his record
                        patient_collection = self.db.patients
                        casey_record_query_result=patient_collection.find_one(CASEY_PATIENT_QUERY)
                        if casey_record_query_result==None:
                                self.fail("Could not find casey's record")                
                        else:                                 
                                print('casey record found: ',casey_record_query_result)
                                #check if record has the photo field; if not, add it
                                patient_collection.update_one(
                                        {'_id':casey_record_query_result.get('_id')},
                                        {'$set':{'photo':img._id}})
                        img.close()

        def test_case12_ICD10(self):
                ICD10_collection = self.db.ICD10
                if ICD10_collection.find_one({})==None:
                        ICD10ListObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/icd10_codes.json")
                        insert_result = ICD10_collection.insert_many(ICD10ListObj)
                        print('ICD10 records inserted: ',insert_result.inserted_ids)                            

if __name__ == '__main__': unittest.main()
