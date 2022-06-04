#!/bin/bash
while read p; do

	  website=`curl -s -N https://markets.money.cnn.com/research/quote/forecasts.asp?symb=$p | grep -A2 -E -m 1 '<div class="wsod_twoCol clearfix">'`
	    annalyst=`echo $website | sed -e 's/.*The \(.*\) analysts offering.*/\1/'`
	      median=`echo $website | sed -e 's/.*median target of \(.*\), with a high.*/\1/'`
	        high=`echo $website | sed -e 's/.*high estimate of \(.*\) and a low.*/\1/'`
		  low=`echo $website | sed -e 's/.*low estimate of \(.*\). The median.*/\1/'`
		    percentage=`echo $website | sed -E 's/.*Data">(.*)%<\/span> .*/\1/'`
		      lastPrice=`echo $website |  sed -e 's/.*from the last price of \(.*\).<\/p><div class="wsod_chart">.*/\1/'`
		        echo here $p$median$low$high$percentage$lastPrice$annalyst
			  mysql -uroot -p'Password' <<EOF
  Use Prediction;
  Insert into NasdaqPredictions Values ('$p',$high,$low,$median,$percentage,$lastPrice,$annalyst);
EOF
done <nasdaqfile
