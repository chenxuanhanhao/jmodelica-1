/*
Copyright (C) 2013 Modelon AB

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

// System includes
#include <iostream>

#include "jccutils.h"
#include "transferModelica.hpp"

// CasADi
#include "casadi/casadi.hpp"

// Wrapped classes from the Modelica compiler
#include "java/lang/System.h"
#include "java/util/ArrayList.h"
#include "java/util/Collection.h"
#include "java/util/LinkedHashMap.h"
#include "java/util/Set.h"
#include "java/util/Iterator.h"
#include "org/jmodelica/modelica/compiler/AliasManager.h"
#include "org/jmodelica/modelica/compiler/ModelicaCompiler.h"
#include "org/jmodelica/modelica/compiler/FDerivedType.h"
#include "org/jmodelica/modelica/compiler/FType.h"
#include "org/jmodelica/modelica/compiler/FAttribute.h"
#include "org/jmodelica/modelica/compiler/FStringComment.h"
#include "org/jmodelica/modelica/compiler/SourceRoot.h"
#include "org/jmodelica/modelica/compiler/InstClassDecl.h"
#include "org/jmodelica/modelica/compiler/FClass.h"
#include "org/jmodelica/modelica/compiler/List.h"
#include "org/jmodelica/modelica/compiler/FAbstractEquation.h"
#include "org/jmodelica/modelica/compiler/FVariable.h"
#include "org/jmodelica/modelica/compiler/FRealVariable.h"
#include "org/jmodelica/modelica/compiler/FDerivativeVariable.h"
#include "org/jmodelica/modelica/compiler/FExp.h"
#include "org/jmodelica/modelica/compiler/FFunctionDecl.h"
#include "org/jmodelica/modelica/compiler/FEquation.h"
#include "org/jmodelica/optimica/compiler/BLT.h"
#include "org/jmodelica/modelica/compiler/StructuredBLT.h"
#include "org/jmodelica/modelica/compiler/AbstractEquationBlock.h"
#include "org/jmodelica/modelica/compiler/SimpleEquationBlock.h"
#include "org/jmodelica/modelica/compiler/ScalarEquationBlock.h"
#include "org/jmodelica/modelica/compiler/SolvedScalarEquationBlock.h"
#include "org/jmodelica/modelica/compiler/EquationBlock.h"
#include "org/jmodelica/modelica/compiler/TornEquationBlock.h"

// Wrapped classes from the Optimica compiler
#include "org/jmodelica/optimica/compiler/AliasManager.h"
#include "org/jmodelica/optimica/compiler/OptimicaCompiler.h"
#include "org/jmodelica/optimica/compiler/FStringComment.h"
#include "org/jmodelica/optimica/compiler/FAttribute.h"
#include "org/jmodelica/optimica/compiler/FDerivedType.h"
#include "org/jmodelica/optimica/compiler/FType.h"
#include "org/jmodelica/optimica/compiler/SourceRoot.h"
#include "org/jmodelica/optimica/compiler/InstClassDecl.h"
#include "org/jmodelica/optimica/compiler/FClass.h"
#include "org/jmodelica/optimica/compiler/FOptClass.h"
#include "org/jmodelica/optimica/compiler/FRelationConstraint.h"
#include "org/jmodelica/optimica/compiler/List.h"
#include "org/jmodelica/optimica/compiler/FAbstractEquation.h"
#include "org/jmodelica/optimica/compiler/FVariable.h"
#include "org/jmodelica/optimica/compiler/FRealVariable.h"
#include "org/jmodelica/optimica/compiler/FDerivativeVariable.h"
#include "org/jmodelica/optimica/compiler/FTimedVariable.h"
#include "org/jmodelica/optimica/compiler/FIdUse.h"
#include "org/jmodelica/optimica/compiler/FExp.h"
#include "org/jmodelica/optimica/compiler/FFunctionDecl.h"
#include "org/jmodelica/optimica/compiler/Root.h"
#include "org/jmodelica/optimica/compiler/BaseNode.h"
#include "org/jmodelica/util/OptionRegistry.h"
#include "org/jmodelica/optimica/compiler/BLT.h"
#include "org/jmodelica/optimica/compiler/StructuredBLT.h"
#include "org/jmodelica/optimica/compiler/FEquation.h"
#include "org/jmodelica/optimica/compiler/AbstractEquationBlock.h"
#include "org/jmodelica/optimica/compiler/SimpleEquationBlock.h"
#include "org/jmodelica/optimica/compiler/ScalarEquationBlock.h"
#include "org/jmodelica/optimica/compiler/SolvedScalarEquationBlock.h"
#include "org/jmodelica/optimica/compiler/EquationBlock.h"
#include "org/jmodelica/optimica/compiler/TornEquationBlock.h"

#include "EquationContainer.hpp"
#include "FlatEquationList.hpp"
#include "BLTContainer.hpp"

// For transforming output from JCC-wrapped classes to CasADi objects. 
// Must be included after FExp.h
#include "mxwrap.hpp" 
#include "mxfunctionwrap.hpp" 
#include "mxvectorwrap.hpp" 

namespace mc = org::jmodelica::modelica::compiler;
namespace jl = java::lang;
using org::jmodelica::util::OptionRegistry;
using std::cout;  using std::endl; using std::string;
using std::vector;

namespace oc = org::jmodelica::optimica::compiler;

namespace ModelicaCasADi {

typedef struct MCStruct
{
        typedef mc::FClass FClass;
        typedef mc::List List;
        typedef mc::FDerivedType FDerivedType;
        typedef mc::FAttribute FAttribute;
        typedef mc::FType FType;
        typedef mc::FRealVariable FRealVariable;
        typedef mc::FVariable FVariable;
        typedef mc::FDerivativeVariable FDerivativeVariable;
        typedef mc::FStringComment FStringComment;
        typedef mc::FAbstractEquation FAbstractEquation;
        typedef mc::FFunctionDecl FFunctionDecl;
        typedef mc::ModelicaCompiler TCompiler;
        typedef mc::FEquation FEquation;
        typedef mc::FExp FExp;
        typedef mc::AbstractEquationBlock TBlock;
        typedef mc::BLT TBLT;
        
}MCStruct;

typedef struct OCStruct
{
        typedef oc::FClass FClass;
        typedef oc::List List;
        typedef oc::FDerivedType FDerivedType;
        typedef oc::FAttribute FAttribute;
        typedef oc::FType FType;
        typedef oc::FRealVariable FRealVariable;
        typedef oc::FVariable FVariable;
        typedef oc::FDerivativeVariable FDerivativeVariable;
        typedef oc::FStringComment FStringComment;
        typedef oc::FAbstractEquation FAbstractEquation;
        typedef oc::FFunctionDecl FFunctionDecl;
        typedef oc::ModelicaCompiler TCompiler;
        typedef oc::FExp FExp;
        typedef oc::FEquation FEquation;
        typedef oc::AbstractEquationBlock TBlock;
        typedef oc::BLT TBLT;
        
}OCStruct;

template <typename CStruct, typename TModel>
void transferModel(Ref<TModel> m, string modelName, const vector<string> &modelFiles,
                        Ref<CompilerOptionsWrapper> options, string log_level, bool with_blt=false)
{
      if(with_blt){
            options->setBooleanOption("automatic_tearing", false);
      }
      typename CStruct::TCompiler compiler(options->getOptionRegistry());
      java::lang::String fileVecJava[modelFiles.size()];
      for (int i = 0; i < modelFiles.size(); ++i) {
            fileVecJava[i] = StringFromUTF(modelFiles[i].c_str());
      }
      compiler.setLogger(StringFromUTF(log_level.c_str()));
      typename CStruct::FClass fclass = compiler.compileModelNoCodeGen(
            new_JArray<java::lang::String>(fileVecJava, modelFiles.size()),
            StringFromUTF(modelName.c_str()));
        
      std::string identfier = env->toString(fclass.nameUnderscore().this$);
      // Initialize the model with the model identfier.
      m->initializeModel(identfier);
      /***** ModelicaCasADi::Model *****/
      // Transfer time variable
      transferTime<typename CStruct::FClass>(m, fclass);
      // Transfer user defined types (also generates base types for the user types). 
      transferUserDefinedTypes<typename CStruct::FClass, typename CStruct::List, typename CStruct::FDerivedType, 
                               typename CStruct::FAttribute, typename CStruct::FType>(m, fclass);
      // Variables
      transferVariables<java::util::ArrayList, typename CStruct::FVariable, typename CStruct::FDerivativeVariable, 
        typename CStruct::FRealVariable, typename CStruct::List, typename CStruct::FAttribute, typename CStruct::FStringComment> (m, fclass.allVariables());

      ModelicaCasADi::Ref<ModelicaCasADi::EquationContainer> eqContainer;
      typename CStruct::TBLT jblt;
      if(with_blt){
            jblt =fclass.getDAEBLT();
            if(jblt.size()>0){
                eqContainer = new ModelicaCasADi::BLTContainer();
            }
            else{
                std::cout<<"The Model does not have a BLT. Transfering list of equations.\n";
                eqContainer = new ModelicaCasADi::FlatEquationList();            
            }
      }
      else{
            eqContainer = new ModelicaCasADi::FlatEquationList();
      }
      
      if(eqContainer->hasBLT()){
            
            transferBLTToContainer<typename CStruct::TBLT,
                        typename CStruct::TBlock,
                        java::util::Collection,
                        java::util::Iterator,
                        typename CStruct::FVariable,
                        typename CStruct::FAbstractEquation,
                        typename CStruct::FEquation,
                        typename CStruct::FExp,
                        JArray>(&jblt, eqContainer, m->getNodeToVariableMap(), false, false);
      }
      else{
            transferDaeEquationsToContainer<java::util::ArrayList, typename CStruct::FAbstractEquation>(eqContainer, fclass.equations());
      }
      
      m->setEquationContainer(eqContainer);
      // Equations
      //transferDaeEquations<java::util::ArrayList, typename CStruct::FAbstractEquation>(m, fclass.equations());
      transferInitialEquations<java::util::ArrayList, typename CStruct::FAbstractEquation>(m, fclass.initialEquations());
      
      // Functions
      transferFunctions<typename CStruct::FClass, typename CStruct::List, typename CStruct::FFunctionDecl>(m, fclass);
}

void transferModelFromModelicaCompiler(Ref<Model> m, string modelName, const vector<string> &modelFiles,
        Ref<CompilerOptionsWrapper> options, string log_level, bool with_blt/*=false*/)
{
        try
        {
           jl::System::initializeClass(false);
           mc::ModelicaCompiler::initializeClass(false);
           transferModel<MCStruct, Model >(m,modelName,modelFiles,options,log_level,with_blt);     
        }
        catch (JavaError e) {
                rethrowJavaException(e);
        }        
        
}

void transferModelFromOptimicaCompiler(Ref<OptimizationProblem> m,
    string modelName, const vector<string> &modelFiles, Ref<CompilerOptionsWrapper> options, string log_level, bool with_blt/*=false*/)
{
        try
        {
           jl::System::initializeClass(false);
           oc::ModelicaCompiler::initializeClass(false);
           transferModel<OCStruct, OptimizationProblem >(m,modelName,modelFiles,options,log_level,with_blt);     
        }
        catch (JavaError e) {
                rethrowJavaException(e);
        }             
}

}; // End namespace
