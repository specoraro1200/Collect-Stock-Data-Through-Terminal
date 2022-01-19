#!/bin/bash

  while read p; do
  #website=`curl -s -N https://finance.yahoo.com/quote/$p/ | grep "left-summary-table"` 
  website=`curl -s -N https://finviz.com/quote.ashx?t=$p`
  #annalyst=`echo $website | sed -e 's/.*="longFmt" value="\(.*\)" active="" data-reactid.*/\1/'`  
  website=`echo $website | sed -e 's/.*>Avg Volume<\(.*\)>Change<.*/\1/'`  
  averageVolume=`echo $website | sed -e 's/.*\/td><td width="8%" class="snapshot-td2" align="left"><b>\(.*\)Current stock price.*/\1/'| sed -e 's/<.*//g'` 
  volume=`echo $website | sed -e 's/.*>Volume<\/td><td width="8%" class="snapshot-td2" align="left"><b>\(.*\)/\1/' | sed -e 's/<.*//g'`
  echo $volume $averageVolume HEEEE
  averageVolume=`numfmt --from=si $averageVolume`
  volume=`echo $volume | sed 's/,//g'`

if [ -z volume ]
then
  continue
fi

  answer=$(echo "scale=15;($volume/$averageVolume)" | bc) 
  echo $answer

if [ 1 -eq "$(echo "$answer > .15" | bc)" ]
then
	echo "f"
fi

echo $p $averageVolume $volume
done <NYSEfile
