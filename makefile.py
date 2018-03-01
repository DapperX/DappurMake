import DappurMake as DPMK

MAKE = DPMK.make()
_ = DPMK.variable
f = DPMK.function
DEP = DPMK.globalDependence
TGT = DPMK.globalTarget

ASM = _("nasm")
LD = _("ld")
CC = _("gcc")
ASMFLAG = _(["-f","elf"])
LDFLAG = _("-static")
CFLAG = _(["-Wall","-Wextra","-Wconversion"],["-fno-builtin","-fno-stack-protector","-fno-asynchronous-unwind-tables"])
MAKE.export(ASM,LD,CC,ASMFLAG,LDFLAG,CFLAG)

DIR_MAIN = f.pwd()
DIR_BIN = DIR_MAIN*"/bin"
DIR_LIB = DIR_MAIN*"/lib"
DIR_INCLUDE = (DIR_MAIN + DIR_LIB)*"/include"
DIR_IMG = _("/mnt")
LIB = _("DPOS_main")
PATH_LIB = (~DIR_LIB + "/lib")*LIB*".a"

BIN_EXT = _("init")
MOD_EXCLUDE = _(BIN_EXT,"bin","include","lib","tool","test")
MOD = "./"/f.dir() - MOD_EXCLUDE


bin_base = _(BIN_EXT,MOD,"test")
MAKE[None] = bin_base.depend("lib")
# MAKE[] = _(bin_base,"lib").do(DPMK.start(TAG))
MAKE["mount"] = _().do("sudo tool/mount.sh")
MAKE["umount"] = _().do("sudo tool/umount.sh")
MAKE["test"] = _(DIR_MAIN).depend(DIR_BIN).do(DEP,TGT)


MAKE.make()