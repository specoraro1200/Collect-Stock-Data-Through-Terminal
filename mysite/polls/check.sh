#!/bin/bash
        website=`curl -s -N https://markets.money.cnn.com/research/quote/forecasts.asp?symb=$1 | grep -A2 -E -m 1 '<div class="wsod_twoCol clearfix">'`
	if [[ "$website" == *"no forecast data"* ]]; then
		  echo "It's there."
		  continue
	fi
	annalyst=`echo $website | sed -e 's/.*The \(.*\) analysts offering.*/\1/'`
	median=`echo $website | sed -e 's/.*median target of \(.*\), with a high.*/\1/'| sed 's/,//g'` 
	high=`echo $website | sed -e 's/.*high estimate of \(.*\) and a low.*/\1/'| sed 's/,//g'`
	low=`echo $website | sed -e 's/.*low estimate of \(.*\). The median.*/\1/'| sed 's/,//g'`
	percentage=`echo $website | sed -E 's/.*Data">(.*)%<\/span> .*/\1/'| sed 's/,//g'`	
        lastPrice=`echo $website |  sed -e 's/.*from the last price of \(.*\).<\/p><div class="wsod_chart">.*/\1/'| sed 's/,//g'`
	echo $p "median" $median "here" $low $high $percentage $lastPrice $annalyst
	psql -t -U "sal" -A -d 'project' -c "insert into data (ticker,high,low,median,percentage,lastprice,annalyst,date) values ('$1',$high,$low,$median,'$percentage',$lastPrice,$annalyst,CURRENT_DATE);"		
