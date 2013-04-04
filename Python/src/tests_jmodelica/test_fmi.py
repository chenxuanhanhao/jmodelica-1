#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Copyright (C) 2010 Modelon AB
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
Module containing the tests for the FMI interface.
"""

import nose
import os
import numpy as N
import sys as S

from tests_jmodelica import testattr, get_files_path
from pymodelica.compiler import compile_fmu
from pyfmi.fmi import FMUModel, FMUException, FMUModelME1, FMUModelCS1, load_fmu
import pyfmi.fmi_algorithm_drivers as ad
from pyfmi.common.core import get_platform_dir
from pyjmi.logger_util import get_structured_fmu_log

path_to_fmus = os.path.join(get_files_path(), 'FMUs')
path_to_fmus_me1 = os.path.join(path_to_fmus,"ME1.0")
path_to_fmus_cs1 = os.path.join(path_to_fmus,"CS1.0")
path_to_mofiles = os.path.join(get_files_path(), 'Modelica')

#THIS IS NOW DONE BY FMIL
#@testattr(fmi = True)
#def test_unzip():
#    """
#    This tests the functionality of the method unzip_FMU.
#    """
#    #FMU
#    fmu = 'bouncingBall.fmu'
#   
#    #Unzip FMU
#    tempnames = unzip_fmu(archive=fmu, path=path_to_fmus)
#    binarydir = tempnames['binaries_dir']
#    xmlfile = tempnames['model_desc']
#    
#    platform = get_platform_dir()
#    assert binarydir.endswith(platform)
#    assert xmlfile.endswith('.xml')
#    
#    nose.tools.assert_raises(IOError,unzip_fmu,'Coupled')
    

class Test_load_fmu:
    """
    This test the functionality of load_fmu method.
    """
    
    @testattr(fmi = True)
    def test_raise_exception(self):
        
        nose.tools.assert_raises(FMUException, load_fmu, "test.fmu")
        nose.tools.assert_raises(FMUException, FMUModelCS1, "Modelica_Mechanics_Rotational_Examples_CoupledClutches_ME.fmu",path_to_fmus_me1)
        nose.tools.assert_raises(FMUException, FMUModelME1, "Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
    
    @testattr(windows = True)
    def test_correct_loading(self):
        
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_ME.fmu",path_to_fmus_me1)
        assert isinstance(model, FMUModelME1)
        
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        assert isinstance(model, FMUModelCS1)
        

class Test_FMUModelBase:
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        name = compile_fmu("NegatedAlias",os.path.join(path_to_mofiles,"NegatedAlias.mo"))
        
    def setUp(self):
        """
        Sets up the test case.
        """
        self.negated_alias  = load_fmu('NegatedAlias.fmu')
        
    @testattr(fmi = True)
    def test_set_get_negated_real(self):
        x,y = self.negated_alias.get("x"),self.negated_alias.get("y")
        nose.tools.assert_almost_equal(x,1.0)
        nose.tools.assert_almost_equal(y,-1.0)
        
        self.negated_alias.set("y",2)
        
        x,y = self.negated_alias.get("x"),self.negated_alias.get("y")
        nose.tools.assert_almost_equal(x,-2.0)
        nose.tools.assert_almost_equal(y,2.0)
        
        self.negated_alias.set("x",3)
        
        x,y = self.negated_alias.get("x"),self.negated_alias.get("y")
        nose.tools.assert_almost_equal(x,3.0)
        nose.tools.assert_almost_equal(y,-3.0)
        
    @testattr(fmi = True)
    def test_set_get_negated_integer(self):
        x,y = self.negated_alias.get("ix"),self.negated_alias.get("iy")
        nose.tools.assert_almost_equal(x,1.0)
        nose.tools.assert_almost_equal(y,-1.0)
        
        self.negated_alias.set("iy",2)
        
        x,y = self.negated_alias.get("ix"),self.negated_alias.get("iy")
        nose.tools.assert_almost_equal(x,-2.0)
        nose.tools.assert_almost_equal(y,2.0)
        
        self.negated_alias.set("ix",3)
        
        x,y = self.negated_alias.get("ix"),self.negated_alias.get("iy")
        nose.tools.assert_almost_equal(x,3.0)
        nose.tools.assert_almost_equal(y,-3.0)
    

class Test_FMUModelCS1:
    """
    This class tests pyfmi.fmi.FMUModelCS1
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        rlc_circuit = compile_fmu("RLC_Circuit",os.path.join(path_to_mofiles,"RLC_Circuit.mo"),target="fmucs")
        rlc_circuit_square = compile_fmu("RLC_Circuit_Square",os.path.join(path_to_mofiles,"RLC_Circuit.mo"),target="fmucs")

    def setUp(self):
        """
        Sets up the test case.
        """
        self.rlc  = load_fmu('RLC_Circuit.fmu')
        self.rlc.initialize()
        self.rlc_square  = load_fmu('RLC_Circuit_Square.fmu')
        self.rlc_square.initialize()

    @testattr(fmi = True)
    def test_version(self):
        """
        This tests the (get)-property of version.
        """
        assert self.rlc._get_version() == '1.0'
        
    @testattr(fmi = True)
    def test_valid_platforms(self):
        """
        This tests the (get)-property of types platform
        """
        assert self.rlc._get_types_platform() == 'standard32'
        
    @testattr(fmi = True)
    def test_simulation_with_reset_cs_2(self):
        """
        Tests a simulation with reset of an JModelica generated CS FMU.
        """
        res1 = self.rlc.simulate(final_time=30)
        resistor_v = res1['resistor.v']
        assert N.abs(resistor_v[-1] - 0.159255008028) < 1e-3
        self.rlc.reset()
        res2 = self.rlc.simulate(final_time=30)        
        resistor_v = res2['resistor.v']
        assert N.abs(resistor_v[-1] - 0.159255008028) < 1e-3
        
    @testattr(fmi = True)
    def test_simulation_with_reset_cs_3(self):
        """
        Tests a simulation with reset of an JModelica generated CS FMU
        with events.
        """
        res1 = self.rlc_square.simulate()
        resistor_v = res1['resistor.v']
        print resistor_v[-1]
        assert N.abs(resistor_v[-1] + 0.233534539103) < 1e-3
        self.rlc_square.reset()
        res2 = self.rlc_square.simulate()        
        resistor_v = res2['resistor.v']
        assert N.abs(resistor_v[-1] + 0.233534539103) < 1e-3
    
    @testattr(windows = True)
    def test_simulation_cs(self):
        
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        res = model.simulate(final_time=1.5)
        assert (res.final("J1.w") - 3.245091100366517) < 1e-4
        
    @testattr(windows = True)
    def test_simulation_with_reset_cs(self):
        
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        res1 = model.simulate(final_time=1.5)
        assert (res1["J1.w"][-1] - 3.245091100366517) < 1e-4
        model.reset()
        res2 = model.simulate(final_time=1.5)
        assert (res2["J1.w"][-1] - 3.245091100366517) < 1e-4
    
    @testattr(windows = True)
    def test_default_experiment(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        
        assert N.abs(model.get_default_experiment_start_time()) < 1e-4
        assert N.abs(model.get_default_experiment_stop_time()-1.5) < 1e-4
        assert N.abs(model.get_default_experiment_tolerance()-0.0001) < 1e-4
    
    
    
    @testattr(windows = True)
    def test_types_platform(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        assert model.types_platform == "standard32"
        
    @testattr(windows = True)
    def test_exception_input_derivatives(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        nose.tools.assert_raises(FMUException, model.set_input_derivatives, "u",1.0,1)
        
    @testattr(windows = True)
    def test_exception_output_derivatives(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_CS.fmu",path_to_fmus_cs1)
        nose.tools.assert_raises(FMUException, model.get_output_derivatives, "u",1)
        
    @testattr(assimulo = True)
    def test_multiple_loadings_and_simulations(self):
        model = load_fmu("bouncingBall.fmu",path_to_fmus_cs1,enable_logging=False)
        res = model.simulate(final_time=1.0)
        h_res = res.final('h')
        
        for i in range(40):
            model = load_fmu("bouncingBall.fmu",os.path.join(path_to_fmus,"CS1.0"),enable_logging=False)
            res = model.simulate(final_time=1.0)
        assert N.abs(h_res - res.final('h')) < 1e-4
    
    @testattr(assimulo = True)
    def test_log_file_name(self):
        model = load_fmu("bouncingBall.fmu",os.path.join(path_to_fmus,"CS1.0"))
        assert os.path.exists("bouncingBall_log.txt")
        model = load_fmu("bouncingBall.fmu",os.path.join(path_to_fmus,"CS1.0"),log_file_name="Test_log.txt")
        assert os.path.exists("Test_log.txt")
        model = FMUModelCS1("bouncingBall.fmu",os.path.join(path_to_fmus,"CS1.0"))
        assert os.path.exists("bouncingBall_log.txt")
        model = FMUModelCS1("bouncingBall.fmu",os.path.join(path_to_fmus,"CS1.0"),log_file_name="Test_log.txt")
        assert os.path.exists("Test_log.txt")
        
    @testattr(stddist = True)
    def test_result_name_file(self):
        
        #rlc_name = compile_fmu("RLC_Circuit",os.path.join(path_to_mofiles,"RLC_Circuit.mo"),target="fmucs")
        rlc = FMUModelCS1("RLC_Circuit.fmu")
        
        res = rlc.simulate()
        
        #Default name
        assert res.result_file == "RLC_Circuit_result.txt"
        assert os.path.exists(res.result_file)
        
        rlc = FMUModelCS1("RLC_Circuit.fmu")
        res = rlc.simulate(options={"result_file_name":
                                    "RLC_Circuit_result_test.txt"})
                                    
        #User defined name
        assert res.result_file == "RLC_Circuit_result_test.txt"
        assert os.path.exists(res.result_file)
    
class Test_FMUModelME1:
    """
    This class tests pyfmi.fmi.FMUModelME1
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        depPar1 = compile_fmu("DepParTests.DepPar1",os.path.join(path_to_mofiles,"DepParTests.mo"))
        
    def setUp(self):
        """
        Sets up the test case.
        """
        self._bounce  = load_fmu('bouncingBall.fmu',path_to_fmus_me1)
        self._dq = load_fmu('dq.fmu',path_to_fmus_me1)
        self._bounce.initialize()
        self._dq.initialize()
        self.dep = load_fmu("DepParTests_DepPar1.fmu")
        self.dep.initialize()
    
    @testattr(assimulo = True)
    def test_log_file_name(self):
        model = load_fmu("bouncingBall.fmu",path_to_fmus_me1)
        assert os.path.exists("bouncingBall_log.txt")
        model = load_fmu("bouncingBall.fmu",path_to_fmus_me1,log_file_name="Test_log.txt")
        assert os.path.exists("Test_log.txt")
        model = FMUModelME1("bouncingBall.fmu",path_to_fmus_me1)
        assert os.path.exists("bouncingBall_log.txt")
        model = FMUModelME1("bouncingBall.fmu",path_to_fmus_me1,log_file_name="Test_log.txt")
        assert os.path.exists("Test_log.txt")
    
    @testattr(stddist = True)
    def test_error_xml(self):
        nose.tools.assert_raises(FMUException,load_fmu,"bouncingBall_modified_xml.fmu",path_to_fmus_me1)
        nose.tools.assert_raises(FMUException,FMUModelME1,"bouncingBall_modified_xml.fmu",path_to_fmus_me1)
    
    @testattr(windows = True)
    def test_default_experiment(self):
        model = load_fmu("Modelica_Mechanics_Rotational_Examples_CoupledClutches_ME.fmu",path_to_fmus_me1)
        
        assert N.abs(model.get_default_experiment_start_time()) < 1e-4
        assert N.abs(model.get_default_experiment_stop_time()-1.5) < 1e-4
        assert N.abs(model.get_default_experiment_tolerance()-0.0001) < 1e-4
    
    @testattr(stddist = True)
    def test_get_variable_by_valueref(self):
        assert "der(v)" == self._bounce.get_variable_by_valueref(3)
        assert "v" == self._bounce.get_variable_by_valueref(2)
        
        nose.tools.assert_raises(FMUException, self._bounce.get_variable_by_valueref,7)
    
    @testattr(assimulo = True)
    def test_multiple_loadings_and_simulations(self):
        model = load_fmu("bouncingBall.fmu",path_to_fmus_me1,enable_logging=False)
        res = model.simulate(final_time=1.0)
        h_res = res.final('h')
        
        for i in range(40):
            model = load_fmu("bouncingBall.fmu",path_to_fmus_me1,enable_logging=False)
            res = model.simulate(final_time=1.0)
        assert N.abs(h_res - res.final('h')) < 1e-4
    
    @testattr(fmi = True)
    def test_init(self):
        """
        This tests the method __init__.
        """
        pass
        
    @testattr(fmi = True)
    def test_model_types_platfrom(self):
        assert self.dep.model_types_platform == "standard32"
    
    @testattr(fmi = True)
    def test_boolean(self):
        """
        This tests the functionality of setting/getting fmiBoolean.
        """
        
        val = self.dep.get(["b1","b2"])
        
        assert val[0]
        assert not val[1]
        
        assert self.dep.get("b1")
        assert not self.dep.get("b2")
        
        self.dep.set("b1", False)
        assert not self.dep.get("b1")
        
        self.dep.set(["b1","b2"],[True,True])
        assert self.dep.get("b1")
        assert self.dep.get("b2")

    @testattr(fmi = True)
    def test_real(self):
        """
        This tests the functionality of setting/getting fmiReal.
        """
        const = self._bounce.get_real([3,4])
        
        nose.tools.assert_almost_equal(const[0],-9.81000000)
        nose.tools.assert_almost_equal(const[1],0.70000000)
        
        const = self._bounce.get(['der(v)','e'])

        nose.tools.assert_almost_equal(const[0],-9.81000000)
        nose.tools.assert_almost_equal(const[1],0.70000000)
    
        self.dep.set("r[1]",1)
        nose.tools.assert_almost_equal(self.dep.get("r[1]"),1.00000)
    
    @testattr(fmi = True)
    def test_integer(self):
        """
        This tests the functionality of setting/getting fmiInteger.
        """

        val = self.dep.get(["N1","N2"])
        
        assert val[0] == 1
        assert val[1] == 1
        
        assert self.dep.get("N1") == 1
        assert self.dep.get("N2") == 1
        
        self.dep.set("N1", 2)
        assert self.dep.get("N1") == 2
        
        self.dep.set(["N1","N2"],[3,2])
        assert self.dep.get("N1") == 3
        assert self.dep.get("N2") == 2
        
        self.dep.set("N1", 4.0)
        assert self.dep.get("N1")==4
        
    @testattr(fmi = True)    
    def test_string(self):
        """
        This tests the functionality of setting/getting fmiString.
        """
        #Cannot be tested with the current models.
        pass 
    
    @testattr(fmi = True)
    def test_t(self):
        """
        This tests the functionality of setting/getting time.
        """
        
        assert self._bounce.time == 0.0
        assert self._dq.time == 0.0
        
        self._bounce.time = 1.0
        
        assert self._bounce.time == 1.0
        
        nose.tools.assert_raises(TypeError, self._bounce._set_time, N.array([1.0,1.0]))
        
        
    @testattr(fmi = True)
    def test_real_x(self):
        """
        This tests the property of the continuous_states.
        """
        nose.tools.assert_raises(FMUException, self._bounce._set_continuous_states,N.array([1.]))
        nose.tools.assert_raises(FMUException, self._dq._set_continuous_states,N.array([1.0,1.0]))
        
        temp = N.array([2.0,1.0])
        self._bounce.continuous_states = temp
        
        nose.tools.assert_almost_equal(self._bounce.continuous_states[0],temp[0])
        nose.tools.assert_almost_equal(self._bounce.continuous_states[1],temp[1])

        
    @testattr(fmi = True)
    def test_real_dx(self):
        """
        This tests the method get_derivative.
        """
        #Bounce
        real_dx = self._bounce.get_derivatives()
        nose.tools.assert_almost_equal(real_dx[0], 0.00000000)
        nose.tools.assert_almost_equal(real_dx[1], -9.810000000)

        self._bounce.continuous_states = N.array([2.,5.])
        real_dx = self._bounce.get_derivatives()
        nose.tools.assert_almost_equal(real_dx[0], 5.000000000)
        nose.tools.assert_almost_equal(real_dx[1], -9.810000000)
        
        #DQ
        real_dx = self._dq.get_derivatives()
        nose.tools.assert_almost_equal(real_dx[0], -1.0000000)
        self._dq.continuous_states = N.array([5.])
        real_dx = self._dq.get_derivatives()
        nose.tools.assert_almost_equal(real_dx[0], -5.0000000)

    @testattr(fmi = True)
    def test_real_x_nominal(self):
        """
        This tests the (get)-property of nominal_continuous_states.
        """
        nominal = self._bounce.nominal_continuous_states
        
        assert nominal[0] == 1.0
        assert nominal[1] == 1.0
        
        nominal = self._dq.nominal_continuous_states
        
        assert nominal[0] == 1.0
    
    @testattr(fmi = True)
    def test_version(self):
        """
        This tests the (get)-property of version.
        """
        assert self._bounce._get_version() == '1.0'
        assert self._dq._get_version() == '1.0'
        
    @testattr(fmi = True)
    def test_valid_platforms(self):
        """
        This tests the (get)-property of model_types_platform
        """
        assert self._bounce.model_types_platform == 'standard32'
        assert self._dq.model_types_platform == 'standard32'
        
    @testattr(fmi = True)
    def test_get_tolerances(self):
        """
        This tests the method get_tolerances.
        """
        [rtol,atol] = self._bounce.get_tolerances()
        
        assert rtol == 0.000001
        nose.tools.assert_almost_equal(atol[0],0.000000010)
        nose.tools.assert_almost_equal(atol[1],0.000000010)
        
        [rtol,atol] = self._dq.get_tolerances()
        
        assert rtol == 0.000001
        nose.tools.assert_almost_equal(atol[0],0.000000010)
        
    @testattr(fmi = True)
    def test_event_indicators(self):
        """
        This tests the method get_event_indicators.
        """
        assert len(self._bounce.get_event_indicators()) == 1
        assert len(self._dq.get_event_indicators()) == 0
        
        event_ind = self._bounce.get_event_indicators()
        nose.tools.assert_almost_equal(event_ind[0],1.0000000000)
        self._bounce.continuous_states = N.array([5.]*2)
        event_ind = self._bounce.get_event_indicators()
        nose.tools.assert_almost_equal(event_ind[0],5.0000000000)
    
    @testattr(fmi = True)
    def test_update_event(self):
        """
        This tests the functionality of the method event_update.
        """
        self._bounce.continuous_states = N.array([1.0,1.0])
        
        self._bounce.event_update()
        
        nose.tools.assert_almost_equal(self._bounce.continuous_states[0],1.0000000000)
        nose.tools.assert_almost_equal(self._bounce.continuous_states[1],-0.7000000000)
        
        self._bounce.event_update()
        
        nose.tools.assert_almost_equal(self._bounce.continuous_states[0],1.0000000000)
        nose.tools.assert_almost_equal(self._bounce.continuous_states[1],0.49000000000)
        
        eInfo = self._bounce.get_event_info()
        
        assert eInfo.nextEventTime == 0.0
        assert eInfo.upcomingTimeEvent == False
        assert eInfo.iterationConverged == True
        assert eInfo.stateValueReferencesChanged == False
        
    @testattr(fmi = True)
    def test_get_continuous_value_references(self):
        """
        This tests the functionality of the method get_state_value_references.
        """
        ref = self._bounce.get_state_value_references()
        
        assert ref[0] == 0
        assert ref[1] == 2
        
        ref = self._dq.get_state_value_references()
        
        assert ref[0] == 0
        
    @testattr(fmi = True)
    def test_ode_get_sizes(self):
        """
        This tests the functionality of the method ode_get_sizes.
        """
        [nCont,nEvent] = self._bounce.get_ode_sizes()
        assert nCont == 2
        assert nEvent == 1
        
        [nCont,nEvent] = self._dq.get_ode_sizes()
        assert nCont == 1
        assert nEvent == 0
    
    @testattr(fmi = True)
    def test_get_name(self):
        """
        This tests the functionality of the method get_name.
        """
        assert self._bounce.get_name() == 'bouncingBall'
        assert self._dq.get_name() == 'dq'
    
    @testattr(fmi = True)
    def test_debug_logging(self):
        """
        This test the attribute debugging.
        """
        model = FMUModelME1('bouncingBall.fmu',path_to_fmus_me1,enable_logging=False)
        model.initialize()
        try:
            model.initialize()
        except FMUException:
            pass
        assert len(model.get_log()) == 0 #Get the current log (empty)
        model = FMUModelME1('bouncingBall.fmu',path_to_fmus_me1,enable_logging=False)
        model.initialize()
        model.set_debug_logging(True) #Activates the logging
        try:
            model.initialize()
        except FMUException:
            pass
        assert len(model.get_log()) > 0 #Get the current log (empty)
        model = FMUModelME1('bouncingBall.fmu',path_to_fmus_me1,enable_logging=True)
        model.initialize()
        try:
            model.initialize()
        except FMUException:
            pass
        assert len(model.get_log()) > 0 #Get the current log (empty)
        
    @testattr(fmi = True)
    def test_get_fmi_options(self):
        """
        Test that simulate_options on an FMU returns the correct options 
        class instance.
        """
        assert isinstance(self._bounce.simulate_options(), ad.AssimuloFMIAlgOptions)
        
    @testattr(fmi = True)
    def test_instantiate_jmu(self):
        """ 
        Test that FMUModel can not be instantiated with a JMU file.
        """
        nose.tools.assert_raises(FMUException,FMUModelME1,'model.jmu')
        
        
class Test_FMI_Compile:
    """
    This class tests pymodelica.compile_fmu compilation functionality.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        pass
        
    def setUp(self):
        """
        Sets up the test case.
        """
        fpath = os.path.join(path_to_mofiles,'RLC_Circuit.mo')
        fmuname = compile_fmu('RLC_Circuit',fpath)
        
        self._model  = FMUModelME1(fmuname)

    @testattr(fmi = True)
    def test_get_version(self):
        """ Test the version property."""
        nose.tools.assert_equal(self._model.version, "1.0")
        
    @testattr(fmi = True)
    def test_get_model_types_platform(self):
        """ Test the model types platform property. """
        nose.tools.assert_equal(self._model.model_types_platform, "standard32")

    @testattr(fmi = True)
    def test_set_compiler_options(self):
        """ Test compiling with compiler options."""
        libdir = os.path.join(get_files_path(), 'MODELICAPATH_test', 'LibLoc1',
            'LibA')
        co = {"index_reduction":True, "equation_sorting":True,
            "extra_lib_dirs":[libdir]}
        compile_fmu('RLC_Circuit', os.path.join(path_to_mofiles,'RLC_Circuit.mo'),
            compiler_options = co)

class TestDiscreteVariableRefs(object):
    """
    Test that variable references for discrete variables are computed correctly
    """

    def __init__(self):
        self._fpath = os.path.join(get_files_path(), 'Modelica', "DiscreteVar.mo")
        self._cpath = "DiscreteVar"
    
    def setUp(self):
        """
        Sets up the test class.
        """
        self.fmu_name = compile_fmu(self._cpath, self._fpath,compiler_options={'compliance_as_warning':True, 'generate_runtime_option_parameters':False})
        self.model = FMUModelME1(self.fmu_name)
        
    @testattr(stddist = True)
    def test_vars_model(self):
       """
       Test that the value references are correct
       """
       nose.tools.assert_equal(self.model._save_real_variables_val[0],0)
       nose.tools.assert_equal(self.model._save_real_variables_val[1],2)

class TestDependentParameters(object):
    """
    Test that dependent variables are recomputed when an independent varaible is set.
    """

    def __init__(self):
        self._fpath = os.path.join(get_files_path(), 'Modelica', "DepPar.mo")
        self._cpath = "DepPar.DepPar1"
    
    def setUp(self):
        """
        Sets up the test class.
        """
        self.fmu_name = compile_fmu(self._cpath, self._fpath)
        self.model = FMUModelME1(self.fmu_name)
        
    @testattr(stddist = True)
    def test_parameter_eval(self):
       """
       Test that the parameters are evaluated correctly.
       """
       self.model.set('p1',2.0)

       p2 = self.model.get('p2')
       p3 = self.model.get('p3')

       nose.tools.assert_almost_equal(p2,4)
       nose.tools.assert_almost_equal(p3,12)

class Test_Logger:
    """
    This class tests the Python interface to the FMI runtime log
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Sets up the test class.
        """
        m =  compile_fmu('LoggerTest',os.path.join(path_to_mofiles,'LoggerTest.mo'),compiler_log_level='i',
                compiler_options={'generate_only_initial_system':True})

    def setUp(self):
        """
        Sets up the test case.
        """
        self.m = load_fmu('LoggerTest.fmu')
        self.m.set_debug_logging(True)
        self.m.set('_log_level',6)
        self.m.set_fmil_log_level(5)

    @testattr(fmi = True)
    def test_log_file(self):
        """
        Test that the log file is parsable
        """

        self.m.set('u1',3)

        self.m.get('u1')
        self.m.set('y1',0.)
        self.m.initialize()
        self.m.get('u1')
        self.m.set('u1',4)
        self.m.get('u1')    
        self.m.get_derivatives()
        self.m.set('y1',0.5)
        self.m.get('x1')
        self.m.set('p',0.5)
        self.m.get('x1')

        d = get_structured_fmu_log('LoggerTest_log.txt')
        
        assert len(d)==8, "Unexpected number of solver invocations"
        assert len(d[0]['block_solves'])==4, "Unexpected number of block solves in first iteration"
