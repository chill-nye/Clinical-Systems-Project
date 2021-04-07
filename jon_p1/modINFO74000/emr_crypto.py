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

import os,hashlib
                
SALT_SEPARATOR=':'

def hash_salt_password(password):
        #generate random salt string
        salt_random_hex_string = os.urandom(32).hex()
        #hashes the concatenation of the salt and password and represents it in hexadecimal                                       
        password_hash_hex_string=hashlib.sha256(salt_random_hex_string.encode() + password.encode()).hexdigest()
        #returns the concatenation of the password hash with the salt
        return password_hash_hex_string + SALT_SEPARATOR + salt_random_hex_string

def check_salt_password(hashed_salted_password, user_password):
        #retrieves the password hash and the salt from the concatenated hexadecimal string
        password_hash_hex_string, salt_random_hex_string = hashed_salted_password.split(SALT_SEPARATOR)
        #hashes the concatenation of the salt and of the user password                                       
        user_pasword_hash_hex=hashlib.sha256(salt_random_hex_string.encode() + user_password.encode()).hexdigest()
        #returns the comparison
        return password_hash_hex_string == user_pasword_hash_hex 
