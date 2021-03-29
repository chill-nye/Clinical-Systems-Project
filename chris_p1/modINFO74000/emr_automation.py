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

from modINFO74000.barcode_reader import BarcodeReader


class BarcodeScanner(BarcodeReader):

  def __init__(self,parent,onMRNRead,onIENRead,onDINRead):

    def onBarcodeDataRead(src,data):
      print("barcode data:",data, ' from source ',src)
      if str(data).startswith("MRN") and onMRNRead!=None:
        onMRNRead(str(data)[3:])
      elif str(data).startswith("IEN") and onIENRead!=None:
        onIENRead(str(data)[3:])
      elif str(data).startswith("DIN") and onDINRead!=None:
        onDINRead(str(data)[3:])

    BarcodeReader.__init__(self,parent,onBarcodeDataReady=onBarcodeDataRead)


