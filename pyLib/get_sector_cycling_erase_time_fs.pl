#!/usr/bin/perl -w

use strict;

use Excel::Writer::XLSX;
my $cyc_t;
my @time_array;
my $cyc_time;
my $i;
my $j;
my $line;
my @col_name = ("B".."FF");
my @cols = ("B".."FF");
my @n=(1..80);
my $DUT=0;
my $cycsum=2;
my $chipsum=0;

my @filename = glob("*.txt"); 

my $xl = Excel::Writer::XLSX->new("sector_erase_cycling.xlsx");

my $xlsheet = $xl->add_worksheet("Sheet1");

my $rptheader = $xl->add_format(); # Add a format
$rptheader->set_bold();
$rptheader->set_size('12');
$rptheader->set_font('Century Gothic');
my $normcell = $xl->add_format(); # Add a format
$normcell->set_size('11');




for (@filename){
	
    my $file = $_;
    open (TXT, "$file") || die $!;
    print "$file\n";
    
while($line=<TXT>){
	if($line=~m/AA\s28\s.*55\s(?<cyc_t>\d+)ms/){
		$cyc_t = $+{cyc_t};
		push @time_array,$cyc_t;
		
	}	
}
	
	my $col=shift @col_name;
	$chipsum+=1;
	$i=1;
foreach(@time_array){
	$i+=1;
	$xlsheet->write ("$col"."$i",$_,$normcell);
	$cycsum+=1;
	}
	close (TXT);
	@time_array=();
	for($a=2;$a<$cycsum;$a++){
	
		$xlsheet->write ("A"."$a","cyc".($a-1),$normcell);
}
$cycsum=2;
}	


for($a=0;$a<$chipsum;$a++){
	  $j=shift @cols;
		$xlsheet->write ("$j".1,"#".(++$DUT),$normcell);
}
	$xl->close();