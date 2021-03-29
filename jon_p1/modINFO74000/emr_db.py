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
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure,AutoReconnect
import gridfs

class MiniEMRMongo:
  client=None
  db=None

  @classmethod
  def connect(cls,uri="mongodb://127.0.0.1:27017"):
    #Connect to MongoDB
    cls.client = MongoClient(uri)
    try:
      #cls.client.admin.command('ismaster')
      #cls.client.admin.command('serverStatus')
      cls.db=cls.client.mini_emr
      print('Connected to MongoDb server')
    except AutoReconnect:
      print("Reconnecting server not available")
    except ConnectionFailure:
      print("MongoDb server not available")

  @classmethod
  def disconnect(cls):
    #clear database object
    cls.client.close()
    cls.db=None        
    print('Disconnected from MongoDb server')

  @classmethod
  def uploadGridFSFile(cls,fname,**kwargs1):
    fs = gridfs.GridFS(cls.db)
    if fs.exists(filename=fname): 
      print("GridFS file exists:",fname)
    else:
      f=open(fname,"br") #b - for binary file!                          
      with fs.new_file(filename=fname,kwargs=kwargs1) as new_gridfs_file: 
        new_gridfs_file.write(f)
        oid=new_gridfs_file._id
        new_gridfs_file.close()           
        f.close()    
    return oid

  @classmethod
  def downloadGridFSFile(cls,fileOId):
    fs = gridfs.GridFS(cls.db)
    with fs.get(fileOId) as gridfs_file:
      print('Found gridfs file to download ',gridfs_file._id)  
      file_data=gridfs_file.read()
      gridfs_file.close()
    return file_data
