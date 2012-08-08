#!/usr/bin/python
import urllib, os, re, sys
import logging
logging.basicConfig(format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s" ,level=1)
log = logging.getLogger('genmakefile')


MakefileTEMPLATE = """\
KERNEL=GENERIC GENERIC.MP

%(patch_definition)s

bin:
\tcd ${WRKSRC}/bin && (${_obj}; ${_cleandir}; ${_depend} && ${_build})

sbin:
\tcd ${WRKSRC}/sbin && (${_obj}; ${_cleandir}; ${_depend} && ${_build})

libc:
\tcd ${WRKSRC}/lib/libc && \\
\t(${_obj}; ${_cleandir}; ${_depend} && ${_build})

#
# Targets starts HERE
#

%(body)s

.include "bsd.binpatch.mk"
"""

UNAME = os.uname()
if UNAME[0] != "OpenBSD":
	# Emulate OpenBSD
	UNAME=('OpenBSD', 'openbsd45-binpatch.neolane.org', '4.4', 'GENERIC.MP#2', 'i386')

def convertbuild(modus):
	ret = []
	i=0
	while i < len(modus):
		l = modus[i]
		if l.startswith('cd '):
			ret.append("cd ${WRKSRC}/"+l.split()[1].replace("../../",""))
		elif l == "make obj": ret.append('${_obj}')
		elif l == "make cleandir": ret.append('${_cleandir}')
		elif l == "make depend": ret.append('${_depend}')
		elif l == "make install": ret.append('${_install}')
		elif l == "make includes": ret.append('${_includes}')
		elif l == "make" and modus[i+1] == "make install":
			ret.append("${_build}")
			i+=1
		elif l == "make -f Makefile.bsd-wrapper obj": ret.append("${_obj_wrp}")
		elif l == "make -f Makefile.bsd-wrapper cleandir": ret.append("${_cleandir_wrp}")
		elif l == "make -f Makefile.bsd-wrapper depend": ret.append("${_depend_wrp}")
		elif l == "make -f Makefile.bsd-wrapper install": ret.append("${_install_wrp}")
		elif l == "make -f Makefile.bsd-wrapper" and modus[i+1]== "make -f Makefile.bsd-wrapper install":
			ret.append("${_build_wrp}")
			i+=1
		else:
			log.warning("Unhandled line: '%s'",l)
			ret.append("(%s)"%l)
		i+=1
	return " && ".join(ret)
	

def parsepatch(pname, cat):
	log.debug('parsepatch: %s\t%s',pname, cat)
	patch = urllib.urlopen("http://ftp.openbsd.org/pub/OpenBSD/patches/%s/%s/%s.patch"%(UNAME[2],cat,pname)).read().replace("        ","\t")
	rfpatch = []
	patchfound = 0
	iskernel = 0
	inmodus=0
	for r in patch.splitlines():
		# Kernel patch
		if "new kernel" in r.lower(): iskernel=1
		
		# Search for a line with "patch -p0 < patchname"
		if r.startswith("\tpatch -p0 < "):
			patchfound = 1
			continue
		# Still no patch command, continue
		if not patchfound: continue
		
		# Ends on code
		if r.startswith("--- ") or r.startswith("Index"): break

		if not rfpatch and r.startswith("\t"):
			inmodus = 1
		if rfpatch and not r.startswith("\t"):
			# No more in modus operandi
			inmodus = 0
			
		if inmodus:
			rfpatch.extend( map(lambda x: x.strip(), r.split("&&")))
	buildlist = convertbuild(rfpatch)
	# Build first line
	fl = [ pname+":" ]
	if iskernel: fl.append( " _kernel")
	return ''.join(fl) + "\n\t"+buildlist

def main():
	errata = urllib.urlopen("http://www.openbsd.org/errata%s.html"%UNAME[2].replace('.','')).read().replace("\r","").replace("\n","")
	RE_patches = re.compile("http://ftp.openbsd.org/pub/OpenBSD/patches/%s/([^\/]+)/(.+)\.patch"%(UNAME[2]) )
	plist = []
	CAT = {}
	for cat, name in RE_patches.findall(errata):
		plist.append([name,cat])
		CAT.setdefault(cat.upper(), []).append(name)
	body = []
	plist.reverse()
	for p in plist:
		body.append(parsepatch(*p))

	

	patch_definition = []
	for c in CAT:
		patch_definition.append("PATCH_%s=%s"%(c," ".join(CAT[c])) )
	
	print MakefileTEMPLATE%({
		"patch_definition": "\n".join(patch_definition),
		"body": "\n".join(body)
		})

if __name__ == "__main__":
	main()
