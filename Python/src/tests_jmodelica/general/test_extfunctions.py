#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2010-2017 Modelon AB
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
Module for testing external function support.
"""
import os, subprocess, shutil
from os.path import join as path

import nose
import fnmatch

from pymodelica import compile_fmu
from pymodelica.common.core import get_platform_dir, create_temp_dir
from pyfmi import load_fmu, FMUModelME2
from pyfmi.fmi import FMUException
from tests_jmodelica import testattr, get_files_path
from tests_jmodelica.general.base_simul import *
from assimulo.solvers.sundials import CVodeError

path_to_mofiles = os.path.join(get_files_path(), 'Modelica')

class TestEvaluator:
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_base = True)
    def test_builtin_substring(self):
        cpath = "ExtFunctionTests.Evaluator_Substring"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, compiler_log_level="d:log.txt")
        
        nbr_of_evaluator_calls = 0
        with open("log.txt") as f:
            res = fnmatch.filter(f, "Succesfully connected external function '*' to the evaluator*")
            nbr_of_evaluator_calls = len(res)
        
        assert nbr_of_evaluator_calls == 4, "Wrong number of external function calls, check log."
        
        model = load_fmu(fmu_name)
        
        assert model.get("sub")[0] == "Y", model.get("sub")
        assert model.get("string2")[0] == "line", model.get("string2")
        assert model.get("len") == 16, model.get("len")
        assert model.get("start") == 4, model.get("start")
        assert not model.get("not_equal"), model.get("not_equal")
        assert model.get("equal"), model.get("equal")
    
    @testattr(stddist_base = True)
    def test_add(self):
        cpath = "ExtFunctionTests.Evaluator_Add"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, version=2.0, compiler_log_level="d:log.txt")
        
        nbr_of_evaluator_calls = 0
        with open("log.txt") as f:
            res = fnmatch.filter(f, "Succesfully connected external function '*' to the evaluator*")
            nbr_of_evaluator_calls = len(res)
        
        assert nbr_of_evaluator_calls == 2, "Wrong number of external function calls, check log."
        
        model = FMUModelME2(fmu_name, _connect_dll=False)
        
        assert model.get_variable_start("c") == 3, model.get_variable_start("c")
        assert model.get_variable_start("d") == 3, model.get_variable_start("d")
    
    @testattr(stddist_base = True)
    def test_unsupported_signature(self):
        cpath = "ExtFunctionTests.Evaluator_Multiple_Add"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, compiler_log_level="d:log.txt")
        
        matches = 0
        with open("log.txt") as f:
            res = fnmatch.filter(f, "*is not supported. Disabling use of the evaluator*")
            matches = len(res)
        
        assert matches == 1, "Does not seem to disabling the evaluator"

    @testattr(stddist_base = True)
    def test_unknown_shared_library(self):
        cpath = "ExtFunctionTests.Evaluator_Unknown_Shared"
        try:
            fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, compiler_log_level="d:log_unknown_shared.txt")
        except: #The compilation will fail, the interesting parts will though still be contained in the log file
            pass
        
        matches = 0
        with open("log_unknown_shared.txt") as f:
            res = fnmatch.filter(f, "Could not find a shared library containing*")
            matches = len(res)
        
        assert matches == 1, "Seems to have found an unknown shared library"
    
    @testattr(stddist_base = True)
    def test_double_return(self):
        cpath = "ExtFunctionTests.Evaluator_Double"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, version=2.0, compiler_log_level="d:log.txt")
        
        nbr_of_evaluator_calls = 0
        with open("log.txt") as f:
            res = fnmatch.filter(f, "Succesfully connected external function '*' to the evaluator*")
            nbr_of_evaluator_calls = len(res)
        
        assert nbr_of_evaluator_calls == 2, "Wrong number of external function calls, check log."
        
        model = FMUModelME2(fmu_name, _connect_dll=False)
        
        assert model.get_variable_start("c") == 3.0, model.get_variable_start("c")
        assert model.get_variable_start("d") == 9.0, model.get_variable_start("d")
    
    @testattr(stddist_base = True)
    def test_integer_return(self):
        cpath = "ExtFunctionTests.Evaluator_Integer"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, version=2.0, compiler_log_level="d:log.txt")
        
        nbr_of_evaluator_calls = 0
        with open("log.txt") as f:
            res = fnmatch.filter(f, "Succesfully connected external function '*' to the evaluator*")
            nbr_of_evaluator_calls = len(res)
        
        assert nbr_of_evaluator_calls == 1, "Wrong number of external function calls, check log."
        
        model = FMUModelME2(fmu_name, _connect_dll=False)
        
        assert model.get_variable_start("c") == 3.0, model.get_variable_start("c")
    
    @testattr(stddist_base = True)
    def test_record(self):
        cpath = "ExtFunctionTests.Evaluator_Record"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"external_constant_evaluation_dynamic":True}, version=2.0, compiler_log_level="d:log.txt")
        
        nbr_of_evaluator_calls = 0
        with open("log.txt") as f:
            res = fnmatch.filter(f, "Succesfully connected external function '*' to the evaluator*")
            nbr_of_evaluator_calls = len(res)
        
        assert nbr_of_evaluator_calls == 1, "Wrong number of external function calls, check log."
        
        model = FMUModelME2(fmu_name, _connect_dll=False)
        
        assert model.get_variable_start("c.x0") == 1.0, model.get_variable_start("c.x0")
        assert model.get_variable_start("c.x1") == 2.0, model.get_variable_start("c.x1")
        assert model.get_variable_start("c.x2") == 3.0, model.get_variable_start("c.x2")
        assert model.get_variable_start("c.x3") == 3.0, model.get_variable_start("c.x3")
        assert model.get_variable_start("c.x4") == 4.0, model.get_variable_start("c.x4")
        assert model.get_variable_start("c.x5") == 5.0, model.get_variable_start("c.x5")
        assert model.get_variable_start("c.x6") == 6.0, model.get_variable_start("c.x6")
        assert model.get_variable_start("c.x7") == 7.0, model.get_variable_start("c.x7")
        assert model.get_variable_start("c.x8") == 8.0, model.get_variable_start("c.x8")
        assert model.get_variable_start("c.x9") == 9.0, model.get_variable_start("c.x9")
        assert model.get_variable_start("c.x10") == 10.0, model.get_variable_start("c.x10")
    
class TestExternalStatic:

    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_base = True)
    def test_ExtFuncStatic(self):
        """ 
        Test compiling a model with external functions in a static library.
        """
        cpath = "ExtFunctionTests.ExtFunctionTest1"
        fmu_name = compile_fmu(cpath, TestExternalStatic.fpath)
        model = load_fmu(fmu_name)
    
    @testattr(stddist_base = True)
    def test_IntegerArrays(self):
        """
        Test a model with external functions containing integer array and literal inputs.
        """
        cpath = "ExtFunctionTests.ExtFunctionTest4"
        fmu_name = compile_fmu(cpath, TestExternalStatic.fpath, compiler_options={'variability_propagation':False})
        model = load_fmu(fmu_name)
        res = model.simulate()
        
        nose.tools.assert_equals(res.final('myResult[1]'), 2) 
        nose.tools.assert_equals(res.final('myResult[2]'), 4)
        nose.tools.assert_equals(res.final('myResult[3]'), 6)
        
class TestUtilities:
    
    @testattr(stddist_base = True)
    def test_ModelicaUtilities(self):
        """ 
        Test compiling a model with external functions using the functions in ModelicaUtilities.
        """
        fpath = path(get_files_path(), 'Modelica', "ExtFunctionTests.mo")
        cpath = "ExtFunctionTests.ExtFunctionTest3"
        fmu_name = compile_fmu(cpath, fpath, compiler_options={'variability_propagation':False})
        model = load_fmu(fmu_name)
        #model.simulate()

class TestExternalShared:
    
    @classmethod
    def setUpClass(self):
        """
        Sets up the test class.
        """
        self.cpath = "ExtFunctionTests.ExtFunctionTest1"
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_base = True)
    def test_ExtFuncShared(self):
        """ 
        Test compiling a model with external functions in a shared library. Simple.
        """
        fmu_name = compile_fmu(self.cpath, self.fpath, compiler_options={'variability_propagation':False})
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('c'), 3) 
        
    @testattr(stddist_base = True)
    def test_ExtFuncSharedCeval(self):
        """ 
        Test compiling a model with external functions in a shared library. Constant evaluation during compilation.
        """
        fmu_name = compile_fmu(self.cpath, self.fpath, compiler_options={'variability_propagation':True})
        model = load_fmu(fmu_name)
        nose.tools.assert_equals(model.get('c'), 3)
        
    @testattr(stddist_full = True)
    def test_ExtFuncSharedCevalDisabled(self):
        """ 
        Test compiling a model with external functions in a shared library. Disabling external evaluation during
        variability propagation.
        """
        fmu_name = compile_fmu(self.cpath, self.fpath, compiler_options={'variability_propagation':True,
            'variability_propagation_external':False})
        model = load_fmu(fmu_name)
        nose.tools.assert_equals(model.get_variable_variability('c'), 1)

class TestExternalBool:
    
    @classmethod
    def setUpClass(self):
        """
        Sets up the test class.
        """
        self.cpath = "ExtFunctionTests.ExtFunctionBool"
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_full = True)
    def test_ExtFuncBool(self):
        """ 
        Test compiling a model with external functions in a shared library. Boolean arrays.
        """
        fmu_name = compile_fmu(self.cpath, self.fpath, compiler_options={'variability_propagation':False})
        model = load_fmu(fmu_name)
        model.simulate()
        trueInd  = {1,2,3,5,8}
        falseInd = {4,6,7}
        for i in trueInd:
            assert(model.get('res[' + str(i) + ']'))
        for i in falseInd:
            assert(not model.get('res[' + str(i) + ']'))

class TestExternalRecord(SimulationTest):
    @classmethod
    def setUpClass(cls):
        SimulationTest.setup_class_base('ExtFunctionTests.mo', 
            'ExtFunctionTests.ExtFunctionRecord')

    @testattr(stddist_full = True)
    def setUp(self):
        self.setup_base(start_time=0.0, final_time=0.1, time_step=0.01)
        self.run()

    @testattr(stddist_full = True)
    def test_result(self):
        self.assert_end_value('y.x', 0.1)

class TestExternalRecordCeval(SimulationTest):
    @classmethod
    def setUpClass(cls):
        SimulationTest.setup_class_base('ExtFunctionTests.mo', 
            'ExtFunctionTests.ExtFunctionRecordCeval')

    @testattr(stddist_full = True)
    def setUp(self):
        self.setup_base(start_time=0.0, final_time=0.1, time_step=0.01)
        self.run()

    @testattr(stddist_full = True)
    def test_result(self):
        self.assert_end_value('y1.x', 3)
        self.assert_end_value('y2.x', 3)


class TestExternalRecordObj(SimulationTest):
    @classmethod
    def setUpClass(cls):
        SimulationTest.setup_class_base('ExtFunctionTests.mo', 
            'ExtFunctionTests.GlobalExtFunctionDestruction')

    @testattr(stddist_full = True)
    def setUp(self):
        self.setup_base(start_time=0.0, final_time=0.1, time_step=0.01)
        self.run()

    @testattr(stddist_full = True)
    def test_result(self):
        pass #We test that there is no segfault when destroying the FMU object

class TestGlobalExternalRecordObj(SimulationTest):
    @classmethod
    def setUpClass(cls):
        SimulationTest.setup_class_base('ExtFunctionTests.mo', 
            'ExtFunctionTests.ExtFunctionRecordObj')

    @testattr(stddist_full = True)
    def setUp(self):
        self.setup_base(start_time=0.0, final_time=0.1, time_step=0.01)
        self.run()

    @testattr(stddist_full = True)
    def test_result(self):
        self.assert_end_value('y', 3)

class TestExternalRecordObjCeval(SimulationTest):
    @classmethod
    def setUpClass(cls):
        SimulationTest.setup_class_base('ExtFunctionTests.mo', 
            'ExtFunctionTests.ExtFunctionRecordObjCeval')

    @testattr(stddist_full = True)
    def setUp(self):
        self.setup_base(start_time=0.0, final_time=0.1, time_step=0.01)
        self.run()

    @testattr(stddist_full = True)
    def test_result(self):
        self.assert_end_value('y', 3)


class TestExternalShared2:
    
    @classmethod
    def setUpClass(self):
        """
        Sets up the test class.
        """
        self.cpath = "ExtFunctionTests.ExtFunctionTest2"
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_base = True)
    def test_ExtFuncShared(self):
        """ 
        Test compiling a model with external functions in a shared library. Real, Integer, and Boolean arrays.
        Compare results between constant evaluation and simulation.
        """
        fmu_name = compile_fmu(self.cpath, self.fpath, compiler_options={'variability_propagation':True})
        model = load_fmu(fmu_name)
        s_ceval = model.get('s')
        res = model.simulate()
        s_sim1 = res.final('s')
        
        fmu_name = compile_fmu(self.cpath, self.fpath, compiler_options={'variability_propagation':False})
        model = load_fmu(fmu_name)
        res = model.simulate()
        s_sim2 = res.final('s')
        nose.tools.assert_equals(s_sim1, s_sim2)
        
class TestExternalInf:
    
    @classmethod
    def setUpClass(self):
        """
        Sets up the test class. Check timeout of infinite loop during constant evaluation.
        """
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_full = True)
    def test_InfiniteLoopExternalEvaluation(self):
        """ 
        Test compiling a model with external functions in a shared library. Infinite loop.
        """
        fmu_name = compile_fmu("ExtFunctionTests.ExternalInfinityTest", self.fpath)
        
    @testattr(stddist_full = True)
    def test_InfiniteLoopExternalEvaluationError(self):
        """ 
        Test compiling a model with external functions in a shared library. Infinite loop.
        """
        try:
            fmu_name = compile_fmu("ExtFunctionTests.ExternalInfinityTestCeval", self.fpath, compiler_options={"external_constant_evaluation":100}, compiler_log_level="e:e.txt")
        except:
            pass
        file=open("e.txt")
        i = 0
        for line in file.readlines():
            if "timed out" in line:
                i = i+1
        assert i == 1, 'Wrong error message'
        
class TestExternalObject:
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_base = True)
    def test_ExtObjectDestructor(self):
        """ 
        Test compiling a model with external object functions in a static library.
        """
        cpath = 'ExtFunctionTests.ExternalObjectTests1'
        fmu_name = compile_fmu(cpath, TestExternalObject.fpath)
        model = load_fmu(fmu_name)
        model.simulate()
        model.terminate()
        if (os.path.exists('test_ext_object.marker')):
             os.remove('test_ext_object.marker')
        else:
            assert False, 'External object destructor not called.'
            
class TestExternalObject2:
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_full = True)
    def test_ExtObjectDestructor(self):
        """ 
        Test compiling a model with external object functions in a static library.
        """
        cpath = 'ExtFunctionTests.ExternalObjectTests2'
        fmu_name = compile_fmu(cpath, TestExternalObject2.fpath)
        model = load_fmu(fmu_name)
        model.simulate()
        model.terminate()
        if (os.path.exists('test_ext_object_array1.marker') and os.path.exists('test_ext_object_array2.marker')):
             os.remove('test_ext_object_array1.marker')
             os.remove('test_ext_object_array2.marker')
        else:
            assert False, 'External object destructor not called.'
            
class TestExternalObject3:
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_full = True)
    def test_ExtObjectDestructor(self):
        cpath = 'ExtFunctionTests.ExternalObjectTests3'
        fmu_name = compile_fmu(cpath, TestExternalObject2.fpath)
        model = load_fmu(fmu_name, log_level=6)
        model.set("_log_level", 6)
        model.simulate()
        model.terminate() #Test that we do not segfault at this point
        log = model.get_log()[-1]
        assert "This should not lead to a segfault" in log
            
class TestExternalObjectConstructorSingleCall:
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_full = True)
    def test_ExtObjectConstructor(self):
        """ 
        Test independent external object constructor is called once 
        """
        cpath = 'ExtFunctionTests.ConstructorSingleCallTest'
        fmu_name = compile_fmu(cpath, TestExternalObjectConstructorSingleCall.fpath)
        model = load_fmu(fmu_name)
        model.simulate()
        model.terminate()

    @testattr(stddist_full = True)
    def test_ExtObjectConstructorDependent(self):
        """ 
        Test external object constructor dependent on parameter is called once 
        """
        cpath = 'ExtFunctionTests.ConstructorSingleCallDepTest'
        fmu_name = compile_fmu(cpath, TestExternalObjectConstructorSingleCall.fpath)
        model = load_fmu(fmu_name)
        model.simulate()
        model.terminate()

    @testattr(stddist_full = True)
    def test_ExtObjectConstructorDependentSetParam(self):
        """ 
        Test external object constructor dependent on parameter is not called when setting parameters
        """
        cpath = 'ExtFunctionTests.ConstructorSingleCallDepTest'
        fmu_name = compile_fmu(cpath, TestExternalObjectConstructorSingleCall.fpath)
        model = load_fmu(fmu_name)
        model.set('s', 'test')
        model.set('s', 'test2')
        model.simulate()
        model.terminate()

class TestAssertEqu3(SimulationTest):
    '''Test structural verification assert'''
    @classmethod
    def setUpClass(cls):
        SimulationTest.setup_class_base(
            "ExtFunctionTests.mo",
            'ExtFunctionTests.StructuralAsserts')
            
    @testattr(stddist_base = True)
    def test_simulate(self):
        try:
            self.setup_base()
            self.run()
            assert False, 'Simulation not stopped by failed assertions'
        except FMUException as e:
            pass
    
class TestModelicaError:
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        cls.fpath = path(path_to_mofiles, 'Asserts.mo')
        
    @testattr(stddist_full = True)
    def test_simulate(self):
        cpath = 'Asserts.ModelicaError'
        fmu_name = compile_fmu(cpath, TestModelicaError.fpath)
        model = load_fmu(fmu_name)
        try:
            model.simulate(final_time = 3, options={"CVode_options":{"minh":1e-15}})
            assert False, 'Simulation not stopped by calls to ModelicaError()'
        except CVodeError as e:
            assert abs(e.t - 2.0) < 0.01, 'Simulation stopped at wrong time'
        

class TestStrings:
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
        
    @testattr(stddist_full = True)
    def testTmpString(self):
        '''
        Test that strings are propagated correctly
        '''
        cpath = "ExtFunctionTests.TestString"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={"variability_propagation":False, "inline_functions":"none"})
        model = load_fmu(fmu_name)
        res = model.simulate() #No asserts should be raised (in the model)

        
class TestCBasic:
    '''
    Test basic external C functions.
    '''
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_full = True)
    def testCEvalReal(self):
        '''
        Constant evaluation of basic external C function with Reals.
        '''
        cpath = "ExtFunctionTests.CEval.C.RealTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('xScalar'), 3*3.14)
        nose.tools.assert_equals(res.final('xArray[2]'), 4)
        nose.tools.assert_equals(res.final('xArrayUnknown[2]'), 6)
        
    @testattr(stddist_full = True)
    def testCEvalInteger(self):
        '''
        Constant evaluation of basic external C function with Integers.
        '''
        cpath = "ExtFunctionTests.CEval.C.IntegerTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('xScalar'), 9)
        nose.tools.assert_equals(res.final('xArray[2]'), 4)
        nose.tools.assert_equals(res.final('xArrayUnknown[2]'), 6)
    
    @testattr(stddist_full = True)
    def testCEvalBoolean(self):
        '''
        Constant evaluation of basic external C function with Booleans.
        '''
        cpath = "ExtFunctionTests.CEval.C.BooleanTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('xScalar'), False)
        nose.tools.assert_equals(res.final('xArray[2]'), True)
        nose.tools.assert_equals(res.final('xArrayUnknown[2]'), False)

    @testattr(stddist_full = True)
    def test_ExtFuncString(self):
        cpath = "ExtFunctionTests.CEval.C.StringTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(model.get('len'), 5)
        #TODO: enable when model.get_string implemented
        #nose.tools.assert_equals(model.get('xScalar'), 'dcb')
        #nose.tools.assert_equals(model.get('xScalarLit'), 'dcb')
        #nose.tools.assert_equals(model.get('xArray[2]'), 'dbf')
        #nose.tools.assert_equals(model.get('xArrayUnknown[2]'), 'dbf')
    
    @testattr(stddist_full = True)
    def testCEvalEnum(self):
        '''
        Constant evaluation of basic external C function with Enums.
        '''
        cpath = "ExtFunctionTests.CEval.C.EnumTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(model.get('xScalar'), 2)
        nose.tools.assert_equals(model.get('xArray[2]'), 2)
        nose.tools.assert_equals(model.get('xArrayUnknown[2]'), 1)
        
    @testattr(stddist_full = True)
    def testCEvalShortClass(self):
        '''
        Constant evaluation of function modified by short class decl
        '''
        cpath = "ExtFunctionTests.CEval.C.ShortClass"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        resConst = model.simulate()
        nose.tools.assert_almost_equal(resConst.final('a1'), 10*3.14)

    @testattr(stddist_full = True)
    def testCEvalPackageConstant(self):
        cpath = "ExtFunctionTests.CEval.C.PackageConstantTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('x[2]'), 4)

class TestFortranBasic:
    '''
    Test basic external fortran functions.
    '''
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_base = True)
    def testCEvalReal(self):
        '''
        Constant evaluation of basic external fortran function with Reals.
        '''
        cpath = "ExtFunctionTests.CEval.Fortran.RealTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('xScalar'), 3*3.14)
        nose.tools.assert_equals(res.final('xArray[2]'), 4)
        nose.tools.assert_equals(res.final('xArrayUnknown[2]'), 6)
        
    @testattr(stddist_base = True)
    def testCEvalMatrixReal(self):
        '''
        Constant evaluation of basic external fortran function with Reals.
        '''
        cpath = "ExtFunctionTests.CEval.Fortran.RealTestMatrix"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('y1[1,1]'), 1)
        nose.tools.assert_equals(res.final('y2[1,1]'), 9)
        
    @testattr(stddist_base = True)
    def testCEvalInteger(self):
        '''
        Constant evaluation of basic external fortran function with Integers.
        '''
        cpath = "ExtFunctionTests.CEval.Fortran.IntegerTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('xScalar'), 9)
        nose.tools.assert_equals(res.final('xArray[2]'), 4)
        nose.tools.assert_equals(res.final('xArrayUnknown[2]'), 6)
    
    @testattr(stddist_full = True)
    def testCEvalBoolean(self):
        '''
        Constant evaluation of basic external fortran function with Booleans.
        '''
        cpath = "ExtFunctionTests.CEval.Fortran.BooleanTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('xScalar'), False)
        nose.tools.assert_equals(res.final('xArray[2]'), True)
        nose.tools.assert_equals(res.final('xArrayUnknown[2]'), False)
    
    @testattr(stddist_full = True)
    def testCEvalEnum(self):
        '''
        Constant evaluation of basic external fortran function with Enums.
        '''
        cpath = "ExtFunctionTests.CEval.Fortran.EnumTest"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(model.get('xScalar'), 2)
        nose.tools.assert_equals(model.get('xArray[2]'), 2)
        nose.tools.assert_equals(model.get('xArrayUnknown[2]'), 1)
        
class TestAdvanced:
    '''
    Test advanced external fortran functions.
    '''
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_base = True)
    def testDGELSX(self):
        '''
        A test using the external fortran function dgelsx from lapack.
        Compares simulation results with constant evaluation results.
        '''
        cpath = "ExtFunctionTests.CEval.Advanced.DgelsxTest"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={'variability_propagation':False})
        model = load_fmu(fmu_name)
        resSim = model.simulate()
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={'variability_propagation':True})
        model = load_fmu(fmu_name)
        resConst = model.simulate()
        for i in range(1,4):
          for j in range(1,4):
            x = 'out[{0},{1}]'.format(i,j)
            nose.tools.assert_almost_equals(resSim.final(x), resConst.final(x), places=13)
        nose.tools.assert_equals(resSim.final('a'), resConst.final('a'))
        nose.tools.assert_equals(resSim.final('b'), resConst.final('b'))
        
    @testattr(stddist_base = True)
    def testExtObjScalar(self):
        '''
        Test constant evaluation of a simple external object.
        '''
        cpath = "ExtFunctionTests.CEval.Advanced.ExtObjTest1"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        resConst = model.simulate()
        nose.tools.assert_equals(resConst.final('x'), 6.13)
        
    @testattr(stddist_base = True)
    def testExtObjArrays(self):
        '''
        Test constant evaluation of arrays of external objects.
        '''
        cpath = "ExtFunctionTests.CEval.Advanced.ExtObjTest2"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        resConst = model.simulate()
        nose.tools.assert_equals(resConst.final('x'), 13.27)
        
    @testattr(stddist_full = True)
    def testExtObjRecursive(self):
        '''
        Test constant evaluation of external object encapsulating 
        external objects.
        '''
        cpath = "ExtFunctionTests.CEval.Advanced.ExtObjTest3"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        resConst = model.simulate()
        nose.tools.assert_equals(resConst.final('x'), 32.67)
    
    @testattr(stddist_full = True)
    def testPartialEvalFail(self):
        '''
        Test failing of partial constant evaluation on external function
        '''
        cpath = "ExtFunctionTests.CEval.Advanced.UnknownInput"
        fmu_name = compile_fmu(cpath, self.fpath, version=1.0) 
        model = load_fmu(fmu_name)
        assert model.get_variable_variability("y") == 3, 'y should be continuous'
        
        fmu_name = compile_fmu(cpath, self.fpath, version=2.0) #Continuous variability is == 4 with FMI2
        model = load_fmu(fmu_name)
        assert model.get_variable_variability("y") == 4, 'y should be continuous'
        
        
    
class TestUtilitiesCEval:
    '''
    Test utility functions in external C functions.
    '''
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_base = True)
    def testCEvalLog(self):
        '''
        Constant evaluation of external C logging function.
        '''
        cpath = "ExtFunctionTests.CEval.Utility.LogTest"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_log_level="w:tmp.log")
        logfile = open('tmp.log')
        count = 0
        for line in logfile:
            if line == "ModelicaMessage: <msg:X is a bit high: 1.100000.>\n" or line == "ModelicaError: <msg:X is too high: 2.100000.>\n":
                count = count + 1
        logfile.close()
        os.remove(logfile.name);
        assert(count >= 2)

class TestCevalCaching:
    '''
    Test caching of external objects during constant evaluation
    '''
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_full = True)
    def testCaching1(self):
        '''
        Test caching of external objects during constant evaluation
        '''
        cpath = "ExtFunctionTests.CEval.Caching.CacheExtObj"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('n3'), 5)
        
    @testattr(stddist_full = True)
    def testCaching2(self):
        '''
        Test caching process limit of external objects during constant evaluation
        '''
        cpath = "ExtFunctionTests.CEval.Caching.CacheExtObjLimit"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={'external_constant_evaluation_max_proc':2})
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('n3'), 20)
        
    @testattr(stddist_full = True)
    def testCaching3(self):
        '''
        Test disabling process caching
        '''
        cpath = "ExtFunctionTests.CEval.Caching.CacheExtObj"
        fmu_name = compile_fmu(cpath, self.fpath, compiler_options={'external_constant_evaluation_max_proc':0})
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('n3'), 4)
        
    @testattr(stddist_full = True)
    def testConError(self):
        '''
        Test caching of external objects during constant evaluation, ModelicaError in constructor.
        '''
        cpath = "ExtFunctionTests.CEval.Caching.ConError"
        fmu_name = compile_fmu(cpath, self.fpath)
        
    @testattr(stddist_full = True)
    def testDeconError(self):
        '''
        Test caching of external objects during constant evaluation, ModelicaError in deconstructor.
        '''
        cpath = "ExtFunctionTests.CEval.Caching.DeconError"
        fmu_name = compile_fmu(cpath, self.fpath)
        
    @testattr(stddist_full = True)
    def testUseError(self):
        '''
        Test caching of external objects during constant evaluation, ModelicaError in use.
        '''
        cpath = "ExtFunctionTests.CEval.Caching.UseError"
        fmu_name = compile_fmu(cpath, self.fpath)
        
        
    @testattr(stddist_full = True)
    def testConCrash(self):
        '''
        Test caching of external objects during constant evaluation, Crash in constructor.
        '''
        cpath = "ExtFunctionTests.CEval.Caching.ConCrash"
        fmu_name = compile_fmu(cpath, self.fpath)
        
    @testattr(stddist_full = True)
    def testDeconCrash(self):
        '''
        Test caching of external objects during constant evaluation, Crash in deconstructor.
        '''
        cpath = "ExtFunctionTests.CEval.Caching.DeconCrash"
        fmu_name = compile_fmu(cpath, self.fpath)
        
    @testattr(stddist_full = True)
    def testUseCrash(self):
        '''
        Test caching of external objects during constant evaluation, Crash in use.
        '''
        cpath = "ExtFunctionTests.CEval.Caching.UseCrash"
        fmu_name = compile_fmu(cpath, self.fpath)
        
class TestMultiUse:
    @classmethod
    def setUpClass(self):
        self.fpath = path(path_to_mofiles, "ExtFunctionTests.mo")
    
    @testattr(stddist_full = True)
    def testMultiUse1(self):
        cpath = "ExtFunctionTests.MultiUse1"
        fmu_name = compile_fmu(cpath, self.fpath)
        model = load_fmu(fmu_name)
        res = model.simulate()
        nose.tools.assert_equals(res.final('y'), 5.0)
