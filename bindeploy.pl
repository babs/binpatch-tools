#!/usr/bin/perl -w

use File::Temp qw/ tempfile tempdir /;

my $tdir = tempdir( CLEANUP => 1 );

# ($fh, $filename) = tempfile( DIR => $tdir );


if ( ! defined $ENV{BINPATCH_URL}) {
    print "Error, the BINPATCH_URL variable is undefined.\n";
    exit(1);
}

# Directories
my @dirlist = qw,/var/db/binpatch /var/db/binpatch/applied /var/db/binpatch/patches /var/db/binpatch/backup,;
foreach ( @dirlist ) {
    mkdir( $_ ) if ( !-d $_ );
}

my $PATCH="/var/db/binpatch/patches";
my $APPLIED="/var/db/binpatch/applied";
my $BACKUP="/var/db/binpatch/backup";

sub help {
    print <<EOF;
$0 update|upgrade
  update: fetch all patch from master server
  upgrade: apply the patch
--
Envireonement;
  BINPATCH_URL: contains your binpatch hosting server
    ex: http://<YOUR_HOST>/openbsd/\$(uname -r)/\$(uname -m)/
EOF
    exit(0);
}

my $URL=$ENV{BINPATCH_URL};

sub trim{
    my $string = shift;
    $string =~ s/^\s+|\s+$//g;
    return $string;
}

sub getVersion {
    open(UNAME, "uname -r|");
    return trim(<UNAME>);
}

sub getArch {
    open(UNAME, "uname -m|");
    return trim(<UNAME>);
}

sub getDirCont {
    my $dir = shift;
    opendir(DIR, $dir);
    my @fnames;
    
    while( ($filename = readdir(DIR) ) ) {
	push(@fnames, $filename) if ( $filename ne "." && $filename ne ".." );
    }
    closedir(DIR);
    return @fnames;
}

sub getPatchList {
    my @patches;
    my $v = getVersion();
    my $a = getArch();

    my $re = "(binpatch-$v-$a-\\d{3}\\.tgz)";

    open(REPO,"ftp -o - $URL 2>/dev/null|");
    while ( <REPO> ) {
	if ( $_ =~ m/$re/ ) {
	    push(@patches, $1);
	}
    }
    return @patches;
}

sub getFile {
    my $url      = shift;
    my $dest     = shift;

    my $arg      = "";
    if ( -e $dest ) {
	$arg = "C";
    }
    system("ftp -mV${arg}o '$dest' '$url'");
}

sub update {
    print " ==== Update patch list. ==== \n";
    my @plist = getPatchList();
    foreach ( @plist ) {
	print " [+] Downloading $URL/$_:\n";
	getFile( $URL."/".$_, $PATCH."/".$_);
	print "\n";
    }
}

sub backup {
    my $patch = shift;
    print " [+] Backup files related to $patch.\n";
    (undef, $tfile ) = tempfile( DIR => $tdir );
    system("tar -ztf $PATCH/$patch > $tfile");
    system("tar -I $tfile -C / -zcvf $BACKUP/$patch");
    print "\n";
}

sub apply {
    my $patch = shift;
    print " [+] Applying $patch.\n";
    system("tar -zvxf $PATCH/$patch -C /");
    open(T, ">>$APPLIED/$patch");
    close(T);
    print "\n";
}

sub upgrade {
    print " ==== Upgrade system. ==== \n";
    my @patches = getDirCont($PATCH);
    foreach ( @patches ) {
	if ( -e $APPLIED."/".$_ ) {
	    print " [-] Patch already applied!\n";
	} else {
	    backup($_);
	    apply($_);
	    print "\n";
	}
    }
}

if ( $#ARGV >= 0 ) {
    if ( $ARGV[0] eq "update" ) {
	update();
    } elsif ( $ARGV[0] eq "upgrade" ) {
	upgrade();
    } else {
	help();
    }
} else {
    help();
}

