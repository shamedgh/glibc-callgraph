#include <iostream>
#include <unordered_map>
#include <bits/stdc++.h> 
#include <fstream>
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Transforms/Utils/BasicBlockUtils.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/IRReader/IRReader.h"
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/GlobalVariable.h"

using namespace llvm;

namespace {

    struct SkeletonPassZero : public ModulePass {
        static char ID;
        SkeletonPassZero() : ModulePass(ID) {}

        virtual bool runOnModule(Module &M) {
            errs() << "In a Module called " << M.getName() << "!\n";
            const char* SYSCALL_STR = "@__syscall_cp";
            const char* SYNCCALL_STR = "@__synccall";
            //errs() << "|||||||||||||||||||||||||||||||||||||\n";
            //errs() << "Function name: " << F.getName() << "\n";
            std::ofstream outfile;
            outfile.open ("callgraph.out", std::ios::out | std::ios::app | std::ios::ate );
            for (auto &Alias : M.getAliasList()){
                    outfile << Alias.getName().str() << "->" << Alias.getAliasee()->getName().str() << "\n";
                    errs() << Alias.getName() << " -> " << Alias.getAliasee()->getName() << "\n";
            }

            int i = 0;
            for (Module::iterator fit = M.begin(), efit = M.end(); fit != efit; ++fit) {
                const Function& F = *fit;
                for (auto &B : F) {
                    for (auto &I : B) {
                        if ( strstr(I.getOpcodeName(), "call" ) != NULL ){
                
    /*                for ( i = 0 ; i < I.getNumOperands(); i++){
                                std::string Str;
                                raw_string_ostream OS(Str);
                                I.getOperand(i)->printAsOperand(OS, false);
                                errs() << i << ":" << OS.str() << "\n";
                            }*/
                            i = I.getNumOperands() - 1;
                            std::string Str;
                            raw_string_ostream OS(Str);
                            I.getOperand(i)->printAsOperand(OS, false);
                            if ( strcmp(OS.str().c_str(), SYSCALL_STR) == 0 || 
                                    strcmp(OS.str().c_str(), "@syscall_cp") == 0 ||
                                    strcmp(OS.str().c_str(), "@syscall") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall0") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall1") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall2") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall3") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall4") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall5") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall6") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall7") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall8") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall9") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall10") == 0 ||
                                    strcmp(OS.str().c_str(), "@__syscall11") == 0 ||
                                    strcmp(OS.str().c_str(), SYSCALL_STR) == 0 ){
                                i = 0;
                                std::string Str;
                                raw_string_ostream OS(Str);
                                I.getOperand(i)->printAsOperand(OS, false);
                                std::string substr = "-";
                                if ( strncmp(OS.str().c_str(), substr.c_str(), substr.size()) == 0 )
                                    errs() << "///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////------------------WE HAVE A NEGATIVE SYSCALL HERE!!!!!!!" << F.getName() << "\n";
//                                errs() << F.getName() << "->syscall(" << OS.str() << ")\n";
                                outfile << F.getName().str().c_str() << "->syscall(" << OS.str().c_str() << ")\n";
                //                outfile << OS.str().c_str() << "hello\n";
                            }else if (strcmp(OS.str().c_str(), SYNCCALL_STR) == 0 ){
                                i = 0;
                                std::string Str;
                                raw_string_ostream OS(Str);
                                I.getOperand(i)->printAsOperand(OS, false);
                                errs() << F.getName() << "->synccall(" << OS.str() << ")\n";
                                outfile << F.getName().str().c_str() << "->" << OS.str().c_str() << "\n";
                                errs() << F.getName() << "->" << OS.str() << "\n";
                            }else{
                                outfile << F.getName().str().c_str() << "->" << OS.str().c_str() << "\n";
                                //errs() << "WARNING: NOT INCLUDING CALLEE: " << OS.str() << "\n";
                            }

                        }	
                    }
                }
            }
            outfile.close();
            return false;
        }


    };

    struct SkeletonPass : public FunctionPass {
        static char ID;
        SkeletonPass() : FunctionPass(ID) {}

        virtual bool runOnFunction(Function &F) {
            std::ofstream outfile;
            outfile.open ("callgraph.out", std::ios::out | std::ios::app | std::ios::ate );
            const char* SYSCALL_STR = "@__syscall_cp";
            const char* SYNCCALL_STR = "@__synccall";
            //errs() << "|||||||||||||||||||||||||||||||||||||\n";
            //errs() << "Function name: " << F.getName() << "\n";
            int i = 0;
            for (auto &B : F) {
                for (auto &I : B) {
                    if ( strstr(I.getOpcodeName(), "call" ) != NULL ){
            
    /*            for ( i = 0 ; i < I.getNumOperands(); i++){
                            std::string Str;
                            raw_string_ostream OS(Str);
                            I.getOperand(i)->printAsOperand(OS, false);
                            errs() << i << ":" << OS.str() << "\n";
                        }*/
                        i = I.getNumOperands() - 1;
                        std::string Str;
                        raw_string_ostream OS(Str);
                        I.getOperand(i)->printAsOperand(OS, false);
                        if ( strcmp(OS.str().c_str(), SYSCALL_STR) == 0 || 
                                strcmp(OS.str().c_str(), "@syscall_cp") == 0 ||
                                strcmp(OS.str().c_str(), "@syscall") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall0") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall1") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall2") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall3") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall4") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall5") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall6") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall7") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall8") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall9") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall10") == 0 ||
                                strcmp(OS.str().c_str(), "@__syscall11") == 0 ||
                                strcmp(OS.str().c_str(), SYSCALL_STR) == 0 ){
                            i = 0;
                            std::string Str;
                            raw_string_ostream OS(Str);
                            I.getOperand(i)->printAsOperand(OS, false);
                            std::string substr = "-";
                            if ( strncmp(OS.str().c_str(), substr.c_str(), substr.size()) == 0 )
                                errs() << "///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////------------------WE HAVE A NEGATIVE SYSCALL HERE!!!!!!!" << F.getName() << "\n";
//                            errs() << F.getName() << "->syscall(" << OS.str() << ")\n";
                            outfile << F.getName().str().c_str() << "->syscall(" << OS.str().c_str() << ")\n";
            //                outfile << OS.str().c_str() << "hello\n";
                        }else if (strcmp(OS.str().c_str(), SYNCCALL_STR) == 0 ){
                            i = 0;
                            std::string Str;
                            raw_string_ostream OS(Str);
                            I.getOperand(i)->printAsOperand(OS, false);
                            errs() << F.getName() << "->synccall(" << OS.str() << ")\n";
                            outfile << F.getName().str().c_str() << "->" << OS.str().c_str() << "\n";
                            errs() << F.getName() << "->" << OS.str() << "\n";
                        }else{
                            outfile << F.getName().str().c_str() << "->" << OS.str().c_str() << "\n";
                            //errs() << "WARNING: NOT INCLUDING CALLEE: " << OS.str() << "\n";
                        }

                    }	
                }
            }

            outfile.close();
            return false;
        }
    };

}


char SkeletonPass::ID = 0;
char SkeletonPassZero::ID = 1;

static RegisterPass<SkeletonPassZero> X("syscall-extract", "Syscall Extraction Pass",
                             false /* Only looks at CFG */,
                             false /* Analysis Pass */);

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerSkeletonPass(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
    PM.add(new SkeletonPass());
}
static void registerSkeletonPassZero(const PassManagerBuilder &, legacy::PassManagerBase &PM) {
    PM.add(new SkeletonPassZero());
}

static RegisterStandardPasses RegisterMyFunctionPass(PassManagerBuilder::EP_EarlyAsPossible, registerSkeletonPass);
//  RegisterMyPass(PassManagerBuilder::EP_OptimizerLast,
static RegisterStandardPasses RegisterMyModulePass(PassManagerBuilder::EP_ModuleOptimizerEarly, registerSkeletonPassZero);
static RegisterStandardPasses RegisterMyModulePass0(PassManagerBuilder::EP_EnabledOnOptLevel0, registerSkeletonPassZero);
