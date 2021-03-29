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

BARCODE_START_KEY_SYMBOL='F11'
BARCODE_STOP_KEY_SYMBOL='F12'

class BarcodeReader():
  _parentWidget=None
  _barcodeData=''
  _readStarted=False
  _onBarcodeDataReady=None
  
  
  def __init__(self,parent,onBarcodeDataReady=None):
    self._parentWidget=parent
    self._onBarcodeDataReady=onBarcodeDataReady

    def key(event):
      if (event.keysym==BARCODE_START_KEY_SYMBOL):
          #print('Barcode start detected')
          self._barcodeData=''
          self._readStarted=True
          #prevent any other widgets getting key events
          self._parentWidget.focus_force()
      elif (event.keysym==BARCODE_STOP_KEY_SYMBOL):
          self._readStarted=False
          #print('Barcode end detected')
          if self._onBarcodeDataReady!=None:
              if self._barcodeData[2]=='-' and self._barcodeData[7]=='-':
                    #source is a barcode scanner with data format [tt]-[ssss]-[ddd....] ,
                    #where t is type, s is serial number and dddd is the scanned data
                    self._onBarcodeDataReady(self._barcodeData[:7],self._barcodeData[8:])
              else: self._onBarcodeDataReady('<kbd>',self._barcodeData)
          else: print("barcode data ready:",self._barcodeData)
          self._barcodeData=''
      elif self._readStarted:
          self._barcodeData+=event.char
      #else: print("key pressed", repr(event.char), "keycode:",event.keycode, 'keysym:',event.keysym)

    self._parentWidget.bind_all("<Key>", key)

