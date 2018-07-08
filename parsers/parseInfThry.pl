use strict;
use warnings;

open(my $out, ">results.csv") or die "didn't open $!";
print $out "bitRotProb;bitsCorrupted;%bitsCorrupted;ValuesCorrupted;%valuesCorrupted;bitsAfterHeal;%bitsAfterHeal;valuesAfterHeal;%valuesAfterHeal;\n";


for (my $j =  1; $j <= 20 ; $j++ ){

	open(my $fh, "<output" . $j . ".txt") or die "file not opened $!";
	
	# throw away junk lines
	<$fh>;<$fh>;<$fh>;<$fh>;<$fh>;<$fh>;<$fh>;<$fh>;<$fh>;

	# getting orig values
	my $line1 = <$fh>;
	my $line2 = <$fh>;
	<$fh>;<$fh>;<$fh>;
	my $line3 = <$fh>;
	my $line4 = <$fh>;
	$line1 .= $line3 . $line2 . $line4; # 1 3 2 4
	my @orig_vals = $line1 =~ /(\d+)/g;
	#print "$_-" foreach @orig_vals;

	<$fh>;<$fh>;<$fh>;<$fh>;<$fh>; <$fh>;

	my $line = '';
	my $l = '';
	for (my $i = 0 ; $i < 6 ; $i++){
		$l = <$fh>;
		$line .= $l;
		<$fh>;<$fh>;<$fh>;
	}
	my @orig_bits = $line =~ /(\d+)/g;
	#print "$_-" foreach @orig_bits;

	#get all data elements
	for (my $i = 1; $i <= 50; $i++){
		#compare
		my $bitsCorrupted = 0;
		my $bitsCorrected = 0; #number of wrong bits after the selfheal
		my $valuesCorrupted = 0;
		my $valuesCorrected = 0; #number of wrongs values after the selfheal

		#print "-----------------------------------------------------------$i\n";
		<$fh>;<$fh>;<$fh>;<$fh>;<$fh>; <$fh>;<$fh>;<$fh>;<$fh>;<$fh>;# throw 10 lines out

		# getting corrupt values
		$line1 = <$fh>;
		$line2 = <$fh>;
		<$fh>;<$fh>;<$fh>;
		$line3 = <$fh>;
		$line4 = <$fh>;
		$line1 .= $line3 . $line2 . $line4;
		my @corrupt_vals = $line1 =~ /(\d+)/g;
		#print "$_-" foreach @corrupt_vals;
		#print "\n\n";

		<$fh>;<$fh>;<$fh>;<$fh>;<$fh>; <$fh>;

		$line = '';
		for (my $j = 0 ; $j < 6 ; $j++){
			$l = <$fh>;
			$line .= $l;
			<$fh>;<$fh>;<$fh>;
		}
		my @corrupt_bits = $line =~ /(\d+)/g;
		#print "$_-" foreach @corrupt_bits;
		#print "\n\n";
		
		# get corrected values
		<$fh>;<$fh>;<$fh>;<$fh>;<$fh>; <$fh>;

		# getting corrected values
		$line1 = <$fh>;
		$line2 = <$fh>;
		<$fh>;<$fh>;<$fh>;
		$line3 = <$fh>;
		$line4 = <$fh>;
		$line1 .= $line3 . $line2 . $line4;
		my @corrected_vals = $line1 =~ /(\d+)/g;
		#print "$_-" foreach @corrected_vals;
		#print "\n\n";
		
		<$fh>;<$fh>;<$fh>;<$fh>;<$fh>; <$fh>;

		$line = '';
		for (my $j = 0; $j < 6 ; $j++){
			$l = <$fh>;
			$line .= $l;
			<$fh>;<$fh>;<$fh>;
		}
		my @corrected_bits = $line =~ /(\d+)/g;
		#print "$_-" foreach @corrected_bits;
		#print "\n\n";

		for (my $j = 0; $j < scalar @orig_bits ; $j++){
			$bitsCorrupted++ if $corrupt_bits[$j]   != $orig_bits[$j];
			$bitsCorrected++ if $corrected_bits[$j] != $orig_bits[$j];
		}

		for (my $j = 0; $j < scalar @orig_vals ; $j++){
			$valuesCorrupted++ if $corrupt_vals[$j] != $orig_vals[$j];
			$valuesCorrected++ if $corrected_vals[$j] != $orig_vals[$j];
		}


		print $out 
			$i/100
			. ";" . $bitsCorrupted 
			. ";" . ($bitsCorrupted*100)/(190)
			
			. ";" . $valuesCorrupted
			. ";" . ($valuesCorrupted*100)/(36)
			
			. ";" . $bitsCorrected
			. ";" . ($bitsCorrected*100)/(190)
			
			. ";" . $valuesCorrected
			. ";" . ($valuesCorrected*100)/(36)
			. "\n";

	}


	close $fh;
}
close $out