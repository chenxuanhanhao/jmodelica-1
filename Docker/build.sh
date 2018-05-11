# 
#    Copyright (C) 2018 Modelon AB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Common Public License as published by
#    IBM, version 1.0 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY. See the Common Public License for more details.
#
#    You should have received a copy of the Common Public License
#    along with this program.  If not, see
#     <http://www.ibm.com/developerworks/library/os-cpl.html/>.

cd JModelica.org
mkdir build
cd build

#added pwd and ls -l for debugging issues with paths to makefiles
pwd
ls -l
#remove 2 lines above
../configure --prefix=/build/jm_install --with-ipopt=/build/ipopt-installation
make install
cd ../..