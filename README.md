binpatch-tools
==============

Those tools can be use to maintain security patches of OpenBSD in conjunction with binpatch.

Binpatch will help you to create packages containing patched sources binnaries.
Those tools will help you to generate the binpatch's Makefile and fetch those patches from your server.

Requirements and usage
----------------------
 * genmakefile.py

This is a Makefile maker, all you need is python on your build machine and a ready to run binpatch deployed.

 * bindeploy

This is the "client" side script which will maintain localy applied patches and backup status and also update from your master server the patch list


Usage
-----
 * genmakefile.py

Just run it where your binpatch arbo is deployed.

 * bindeploy
   
     * update

          This command need a BINPATCH_URL environement variable containing your packages repositories.
 ex: http://my-obsd.patch.server/openbsd/4.5/i386/

     * upgrade
	 	  
		  This command will apply patches them if needed. (and perform a backup before)

Please note that the patches are not easily revertable, because they are binnaries tarballs ex:

 * Patch 001 patches kernel (will backup original kernel)
 * Patch 002 also patches kernel (will backup Patch's 001 kernel)
 * Patch 003 also patches kernel (will backup Patch's 002 kernel)

So if you revert patch 2, you will not have the lastest kernel without the patch 2 :D but the Patch 001's kernel.

### IT'S NOT recommended to REVERT a patch except if you know what you're doing. ###
