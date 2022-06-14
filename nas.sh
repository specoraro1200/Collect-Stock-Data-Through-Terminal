#!/bin/bash
store=$(date +%F)
echo $store
while read p; do

        website=`curl -s -N https://markets.money.cnn.com/research/quote/forecasts.asp?symb=$p | grep -A2 -E -m 1 '<div class="wsod_twoCol clearfix">'`
	#echo $website
	if [[ "$website" == *"no forecast data"* ]]; then
		  echo "It's there."
		  continue
	fi
	#real=`echo $website | sed -e 's/.*"ToHundredth" streamFeed="BatsUS">\(.*\)<\/span><div class="wsod_quoteLabel">Delayed Data<div class="wsod_quoteLabelAsOf".*/\1/'`
	#echo $real
	annalyst=`echo $website | sed -e 's/.*The \(.*\) analysts offering.*/\1/'`
	median=`echo $website | sed -e 's/.*median target of \(.*\), with a high.*/\1/'| sed 's/,//g'` 
	high=`echo $website | sed -e 's/.*high estimate of \(.*\) and a low.*/\1/'| sed 's/,//g'`
	low=`echo $website | sed -e 's/.*low estimate of \(.*\). The median.*/\1/'| sed 's/,//g'`
	percentage=`echo $website | sed -E 's/.*Data">(.*)%<\/span> .*/\1/'| sed 's/,//g'`
	
        lastPrice=`echo $website |  sed -e 's/.*from the last price of \(.*\).<\/p><div class="wsod_chart">.*/\1/'| sed 's/,//g'`
	echo $p "median" $median "here" $low $high $percentage $lastPrice $annalyst
	psql -t -U "sal" -A -d 'project' -c "insert into data (ticker,high,low,median,percentage,lastprice,annalyst,date) values ('$p',$high,$low,$median,'$percentage',$lastPrice,$annalyst,CURRENT_DATE);"
	
#mysql -uroot -p'Password' <<EOF
  #Use Prediction;
  #Insert into NasdaqPredictions Values ('$p',$high,$low,$median,$percentage,$lastPrice,$annalyst);
#EOF
done <list.csv
