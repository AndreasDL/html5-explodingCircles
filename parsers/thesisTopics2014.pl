#!/bin/perl
use strict;
use warnings;

#parse all master thesis topics into fast overview for filtering
my $url = "";
my $output = 'thesis.csv';
my $choicesOutput = 'choices.csv';
my $chosenTopics = 'chosen.csv';

my %userToChoice; # userToChoice[username] = ('choice1', choice2, choice3)
my %topicToUser; # topidToUser[topic] = ( @firstchoices, @secondchoices, @thirdchoices );

open FILE, ">$output";
print FILE "title;numOfStud;location;promotor1;promotor2;assistant1;assistant2;url\n";

foreach (`wget '$url' -O - -q` =~ /<a href=['"]([^'"]*)['"]/g){
	if ($_ =~ /bekijken2*/){
		my $url = 'http://plato.fea.ugent.be/masterproef/studenten/' . $_;
		print "handling $url\n";

		my $topicPage = `wget '$url' -O - -q`;

		my $title = "niet gevonden!";
		$title = $1 if ($topicPage =~ /<h1>([^<]*)<\/h1>/);
		print "\ttitle: $title \n";

		my $promotor1  = "niet gevonden!";
		$promotor1 = $1 if ($topicPage =~ /<td ?>Promotor 1:<\/td><td ?>([^<&]*)/);
		print "\tPromotor 1: $promotor1\n";

		my $promotor2  = "";
		$promotor2 = $1 if ($topicPage =~ /<td ?>Promotor 2:<\/td><td ?>([^<&]*)/);
		print "\tPromotor 2: $promotor2\n";

		my $assistant1  = "niet gevonden!";
		$assistant1 = $1 if ($topicPage =~ /<td ?>Begeleider 1:<\/td><td ?>([^<&]*)/);
		print "\tAssistant 1: $assistant1\n";

		my $assistant2  = "";
		$assistant2 = $1 if ($topicPage =~ /<td ?>Begeleider 2:<\/td><td ?>([^<&]*)/);
		print "\tAssistant 2: $assistant2\n";

		my $numOfStud = "niet gevonden!";
		$numOfStud = $1 if ($topicPage =~ /<td ?>Aantal studenten: <\/td><td ?>([^<&]*)/);
		print "\tNumber Of students: $numOfStud\n";

		my $location = "niet gevonden!";
		$location = "$1" . " - " . "$2" if ($topicPage =~ /<h4>Locatie:<\/h4>\n<p>([^<]*)<\/p>\n<p>([^<]*)/m);
		print "\tLocation: $location\n";

		my @firstChoices = ();
		my $firstChoice = "";
		$firstChoice = "$1" if ($topicPage =~ /<li>Als 1e keuze: (.*?)<li>/m);
		my $i = 0;
		foreach ($firstChoice =~ /([^&]*)&nbsp;/g){
			if ($i % 7 == 0){
				push @firstChoices, $_;
				$userToChoice{$_} = (undef,undef,undef) if (! exists $userToChoice{$_});
				$userToChoice{$_}[0] = $title;
			}
			$i++;
		}
		print "\tfirstChoice: $_\n" foreach @firstChoices;

		my @secondChoices = ();
		my $secondChoice = "";
		$secondChoice = "$1" if ($topicPage =~ /<li>Als 2e keuze: (.*?)<li>/m);
		$i = 0;
		foreach ($secondChoice =~ /([^&]*)&nbsp;/g){
			if ($i % 7 == 0){
				push @secondChoices, $_;
				$userToChoice{$_} = (undef,undef,undef) if (! exists $userToChoice{$_});
				$userToChoice{$_}[1] = $title;
			}
			$i++;
		}
		print "\tsecondChoice: $_\n" foreach @secondChoices;

		my @thirdChoices = ();
		my $thirdChoice = "";
		$thirdChoice = "$1" if ($topicPage =~ /Als 3e keuze: (.*)<\/ul>/m);
		$i = 0;
		foreach ($thirdChoice =~ /([^&]*)&nbsp;/gm){
			if ($i % 7 == 0){
				push @thirdChoices, $_;
				$userToChoice{$_} = (undef,undef,undef) if (! exists $userToChoice{$_});
				$userToChoice{$_}[2] = $title;
			}
			$i++;
		}
		print "\tthirdChoice: $_\n" foreach @thirdChoices;

		#init to 3 emtpy arrays
		$topicToUser{$title} = (undef,undef,undef);
		$topicToUser{$title}[0] = \@firstChoices;
		$topicToUser{$title}[1] = \@secondChoices;
		$topicToUser{$title}[2] = \@thirdChoices;
		print FILE "$title;$numOfStud;$location;$promotor1;$promotor2;$assistant1;$assistant2;$url\n";
	}
}
close FILE;


open FILE, ">$choicesOutput";
print "Printen second sheet - user to topic";
print FILE "name;firstChoice;secondChoice;thirdChoice;\n";
foreach my $k (sort keys %userToChoice){
	print FILE "$k;$userToChoice{$k}[0];$userToChoice{$k}[1];$userToChoice{$k}[2];\n"
}
close FILE;

open FILE, ">$chosenTopics";
print FILE "topic;first;second;third\n";
foreach my $k (sort keys %topicToUser){
	my $line = "$k;";
	
	for (my $i; $i < 3; $i++){
		$line .= "$_ - " foreach (sort @{$topicToUser{$k}[$i]});
		$line .= ";";
	}
	print FILE "$line\n";
}
close FILE;
