'''
    Copyright (C) 2019 Stefan V. Pantazi (svpantazi@gmail.com)    
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
'''
import json
import modINFO74000.emr_const as EMR_CONSTS

PATH_TO_JSON_FILES=EMR_CONSTS.PATH_TO_JSON_FILES
PATH_TO_IMAGE_FILES=EMR_CONSTS.PATH_TO_IMAGE_FILES

'''A very specific function that processes a file in PATH_TO_JSON_FILES/json_test1.txt with CD orders in a very specific way.'''
def ParseCDOrderJSONString_GenerateJSON_AddNorahCD_CalculateTotalCost():
    try:
    #read the json string   
        json_file=open(PATH_TO_JSON_FILES+"/json_test1.txt")
            # load and try to parse the input string
        data=json.load(json_file)
        json_file.close()
    except (FileNotFoundError):
        print("BOO! Error loading json file ")
    else:
        #success    
        #get a reference of the cd list object
        cd_list=data["order"]["items"]["compact-disk"]
        #add a new compact disk to the order
        cd_list.append({
            "price":	"29.95",
            "artist":	"Norah Jones",
            "title":	"Don't Know Why"
        })
        #calculate the total cost
        totalCost=0
        #iterate through the cd list items to add to the total cost
        for cd in cd_list[:]:
            totalCost+=float(cd["price"])
        return totalCost


'''
    A more generic version of the the CD order function
    It loads a JSON file with any file name, opens it, parses it, 
    inserts a new compact disk record for any artist, title and price.
    As before, it calculates and returns the total cost of the order.
    :) Still relies on particular location (order/items/compact-disk) of cd item list in the data 
    Parameters:
        file_name - the name of the JSON file with the CD orders
        artist - the name of the artist
        title - the title of the artist CD album
        price - the price of the CD
    Returns
        total cost of the order
'''
def ParseCDOrderJSONFile_AddCDOrder_CalculateTotalCost(file_name,artist,title,price):
    try:
        json_file=open(file_name)
        data=json.load(json_file)
        json_file.close()
    except (FileNotFoundError):
        print("BOO! Error loading json file ",file_name)
    else:
        cd_list=data["order"]["items"]["compact-disk"]
        cd_list.append({
            "price":	price,
            "artist":	artist,
            "title":	title
        })
        totalCost=0
        for cd in cd_list[:]:
            totalCost+=float(cd["price"])
        return totalCost


'''
    This is the most generic version. The original function was split into 3 separate
    generic function calls.

    1) LoadObjectFromJSONFile loads a JSON file with any file name, opens it, parses it
    and returns an object.

    2) AddObjectToList inserts an object into a list object located at the path
    indicated by the path argument. 
    As an example, it can be used to insert a new compact disk record 
    for any artist, title and price into an array of objects.

    3) CalculateObjectListPropertySum takes an array object, iterates through all its elements
    and calculates a sum of the property indicated by the property name parameter.
    As an example, it can be used to calculate toe the total cost of the CD order array.
    '''
def LoadObjectFromJSONFile(file_name):
    try:
        json_file=open(file_name)
        data=json.load(json_file)
        json_file.close()
    except (FileNotFoundError):
        print("BOO! Error loading json file ",file_name)
        return None
    else:
        return data
'''
Takes an object and an object path to a list of objects and adds the new object to the list.  
'''
def AddObjectToList(root_obj,path,object_to_add):
    root=root_obj
    for s in path:
        root=root[s]
    root.append(object_to_add)
    return root

'''
Takes an object list and a property name, iterates through all objects and sums the values of the property.
'''
def CalculateObjectListPropertySum(object_list,property_name):
    sum=0
    for o in object_list[:]:
        sum+=float(o[property_name])
    return sum

'''Naive implementation of a function that counts objects with a certain property in a list of objects'''
def CountObjectsWithProperty(object_list,property_name,property_value):
    count=0
    for o in object_list:
        if o[property_name]==property_value:
            count=count+1 
    return count

'''A better implementation of counting objects using the filter function
http://www.u.arizona.edu/~erdmann/mse350/topics/list_comprehensions.html'''
def CountObjects(object_list,filter_func):
    map_obj=filter(filter_func,object_list)
    filtered_list=list(map_obj)
    #print(filtered_list)
    return len(filtered_list)

