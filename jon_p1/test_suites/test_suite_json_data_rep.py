#unit tests
#file name must contain the sequence "test" in its file name so that tests are autodiscovered
#tests methods must start with "test_" in order to be discovered and ran automatically 
#https://docs.python.org/3/library/unittest.html

import unittest
#fix for importing a module in a different location
from import_help import modINFO74000
import modINFO74000.misc_func as misc
from modINFO74000.misc_func import PATH_TO_JSON_FILES


def setUpModule():
        print("----- JSON data representation unitest Suite begins")
def tearDownModule():        
        print("\n----- JSON data representation unitest Suite ends")

#CD order processing test suite
class CDOrderTestSuite(unittest.TestCase):

        def test_case00(self):
                """This is a dummy test it does nothing except proving that the testing framework works!"""
                self.assertTrue(True,"always true")

        def test_case01(self):
                """Testing for the equality between what the function returns and the total cost of $64.45"""
                self.assertEqual(
                        misc.ParseCDOrderJSONString_GenerateJSON_AddNorahCD_CalculateTotalCost(),
                        64.45,                        
                        "should have returned a total cost of $64.45 after adding Norah Jones CD") 

        def test_case02(self):
                """Test for equality between what the new, more generic function returns and the total cost of $49.5"""
                self.assertEqual(
                        misc.ParseCDOrderJSONFile_AddCDOrder_CalculateTotalCost(PATH_TO_JSON_FILES+"/json_test1.txt","Taylor Swift","Reputation",15.00),
                        49.5,
                        "should have returned a total cost of $49.50 after adding Taylor Swift CD to the orders") 
        
        def test_case03(self):
                """Test for equality between what the new, more generic function returns and the total cost of $48.53"""
                self.assertEqual(
                        misc.ParseCDOrderJSONFile_AddCDOrder_CalculateTotalCost(PATH_TO_JSON_FILES+"/CD_orders.json","Justin Timberlake","Man of the Woods",14.03),
                        48.53,
                        "should have returned a total cost of $48.53 after adding Justin Timberlake CD to the orders")

        def test_case04(self):
                """Test for equality between what the new, most generic implementation returns and the total cost of $48.53"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/CD_orders.json")
                newArtist={"artist":"Justin Timberlake",
                           "title":"Man of the Woods",
                           "price":14.03}
                arrayObj=misc.AddObjectToList(jsonObj,["order","items","compact-disk"],newArtist)
                self.assertEqual(
                        misc.CalculateObjectListPropertySum(arrayObj,"price"),
                        48.53,
                        "should have returned a total cost of $48.53 after adding Justin Timberlake CD to the orders, using the most general implementation")


#healthcare related test suite
class HealthcareTestSuite(unittest.TestCase):

        def test_case_load_employee(self):
                """Test for employee records json loading"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/empl.json")       
                #for e in jsonObj: print(e)         
                self.assertEqual(len(jsonObj),136,"should have returned 136")

        def test_case_object_count_v1(self):
                """Test for CountObjectsWithProperty function - counting analysts"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/empl.json")                
                numOfAnalysts=misc.CountObjectsWithProperty(jsonObj,"title","ANALYST")
                self.assertEqual(numOfAnalysts,10,"should have returned 10")


        def test_case_object_count_v1_5(self):
                """Test for CountObjectsWithProperty function - counting physicians"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/empl.json")                
                numOfPhysicians=misc.CountObjectsWithProperty(jsonObj,"title","Physician")
                self.assertEqual(numOfPhysicians,20,"should have returned 20")


        def test_case_object_count_v2(self):
                """Test for CountObjects function - counting physicians whose last name starts with DOCTOR"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/empl.json")                
                filter_function=(lambda
                        o: o["title"]=="Physician" and str(o["full_name"]).startswith("DOCTOR")
                        )
                numOfPhysiciansInDOCTORFamily=misc.CountObjects(jsonObj,filter_function)
                self.assertEqual(numOfPhysiciansInDOCTORFamily,12,"should have returned 12")
       
        def test_case_load_jane_doe(self):
                """Test for Jane Doe record json loading"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/000000011.json")                
                self.assertEqual(jsonObj["patient"]["Name"],"DOE,JANE","should have returned DOE,JANE") 

        def test_case_load_vitals_check_bp(self):
                """Test for loading vitals and checking the BP value"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/5.json")    
                bpVal=None  
                for v in jsonObj["vitals"]: 
                        if v["type"]=="BP": 
                                bpVal=v["value"]   
                                break       
                self.assertEqual(bpVal,"120/80","should load the 5.json with vitals data, retrieve the BP value and check its value")

        def test_case_load_vitals_by_index(self):
                """Test for loading vitals by index"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/5.json")    
                #from the vitals array object, get vital data object with index 4
                vitalObjAtIndex4=jsonObj["vitals"][4] 
                #print("Retrieved vital object ",vitalObjAtIndex4["type"],", value: ",vitalObjAtIndex4["value"])
                self.assertEqual("HT",vitalObjAtIndex4["type"],"Type of vital data at index 4 is HT")    
                self.assertEqual("50",vitalObjAtIndex4["value"],"Value of vital data at index 4 is 50")        
    
                #from the vitals array object, get vital data object with index 5
                vitalObjAtIndex5=jsonObj["vitals"][5] 
                #print("Retrieved vital object ",vitalObjAtIndex5["type"],", value: "+vitalObjAtIndex5["value"])
                self.assertEqual("WT",vitalObjAtIndex5["type"],"Type of vital data at index 5 is WT")    
                self.assertEqual("100",vitalObjAtIndex5["value"],"Value of vital data at index 5 is 100")        

                #from the vitals array object, get vital data object with index 7
                vitalObjAtIndex5=jsonObj["vitals"][7] 
                #print("Retrieved vital object ",vitalObjAtIndex5["type"],", value: "+vitalObjAtIndex5["value"])
                self.assertEqual("POX",vitalObjAtIndex5["type"],"Type of vital data at index 7 is POX")    
                self.assertEqual("10",vitalObjAtIndex5["value"],"Value of vital data at index 7 is 10")        


        def test_case_load_drug_data(self):
                """Test for drug data json loading"""
                jsonObj=misc.LoadObjectFromJSONFile(PATH_TO_JSON_FILES+"/drug_data.json")         
                #for d in jsonObj["DrugReport"]: print(d)      #careful with printing this - the file is large          
                self.assertEqual(len(jsonObj["DrugReport"]),23832,"should have returned 23832 as there are this many drugs in the report")


if __name__ == '__main__':  unittest.main()
