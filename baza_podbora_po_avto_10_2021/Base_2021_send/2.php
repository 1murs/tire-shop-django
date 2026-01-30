<?php
include_once "db.php";

$vendors  = array ();

#получение списка вендоров
$result= SQL("SELECT DISTINCT vendor FROM `$db_name`.`$table_name` ORDER BY `$table_name`.`vendor` ASC;");
	if(mysqli_num_rows($result))  { 
		while($row = mysqli_fetch_array($result)) {
		$vendors[]  = $row['vendor'];
	}
}


$xajaxargs = @$_POST['xajaxargs'] ;
$xajax = @$_POST['xajax'] ;

$show = @$_POST['show'] ;
$model_id = @$_POST['modification'];

if ($show == "OK") {

	header("Content-type: text/html; charset=utf-8"); 


	if ($model_id == "") die("<b><center>Ошибка, не полностью выбраны данные для подбора,<br> вернитесь назад и укажите все данные полностью (производитель, марка, год выпуска, модификация)");

	$result= SQL("SELECT * FROM `$db_name`.`$table_name` WHERE id = '" . addslashes($model_id) . "';");

	if(mysqli_num_rows($result))  { 
		$row = mysqli_fetch_array($result);

		$vendor  = $row['vendor'];
		$car  = $row['car'];
		$year  = $row['year'];
		$modification = $row['modification'];

		$zavod_shini = $row['zavod_shini'];
		$zamen_shini = $row['zamen_shini'];
		$tuning_shini = $row['tuning_shini'];
 
		$pcd = $row['pcd'];
		$diametr = $row['diametr'];
		$gaika = $row['gaika'];

		$zavod_diskov = $row['zavod_diskov'];
		$zamen_diskov = $row['zamen_diskov'];
		$tuning_diski = $row['tuning_diski'];

 
 		echo "Подбор дисков и шин для автомобиля <b>$vendor $car $year $modification</b><br><br>\r\n";
		echo "<TABLE BORDER=0>\r\n";
 		echo "<TR><TD><b><center>Параметры шин</center></b></TD></TR>\r\n";

		if ($zavod_shini != "") {
	 		echo "<TR><TD><center>заводская комплектация</center></TD></TR>\r\n";

			$zavod_shini_ = explode('|',$zavod_shini);
			
			for ($j=0; $j<count($zavod_shini_); $j++) {
				$zavod_shini__ = explode('#',$zavod_shini_[$j]);
					if (count($zavod_shini__) >= 2 ) {
						echo "<TR><TD>передняя ось: " . $zavod_shini__[0] . " задняя ось: " . $zavod_shini__[1] . "</TD></TR>\r\n";
					} else {
						echo "<TR><TD>" . $zavod_shini_[$j] . "</TD></TR>\r\n";
					}
			}

		}
		
		if ($zamen_shini != "") {
			echo "<TR><TD><center>варианты замены</center></TD></TR>\r\n";

			$zamen_shini_ = explode('|',$zamen_shini);

			for ($j=0; $j<count($zamen_shini_); $j++) {
				$zamen_shini__ = explode('#',$zamen_shini_[$j]);
					if (count($zamen_shini__) >= 2 ) {
						echo "<TR><TD>передняя ось: " . $zamen_shini__[0] . " задняя ось: " . $zamen_shini__[1] . "</TD></TR>\r\n";
					} else {
						echo "<TR><TD>" . $zamen_shini_[$j] . "</TD></TR>\r\n";
					}
			}

		}

		if ($tuning_shini != "") {
			echo "<TR><TD><center>тюнинг</center></TD></TR>\r\n";
			$tuning_shini_ = explode('|',$tuning_shini);
			for ($j=0; $j<count($tuning_shini_); $j++) {
				$tuning_shini__ = explode('#',$tuning_shini_[$j]);
					if (count($tuning_shini__) >= 2 ) {
						echo "<TR><TD>передняя ось: " . $tuning_shini__[0] . " задняя ось: " . $tuning_shini__[1] . "</TD></TR>\r\n";
					} else {
						echo "<TR><TD>" . $tuning_shini_[$j] . "</TD></TR>\r\n";
					}
			}
		#echo "<br><br>\r\n";
		}

      

 		echo "<TR><TD><b><center>Параметры дисков</center></b></TD></TR>\r\n";
		echo "<TR><TD>PCD: $pcd; диаметр: $diametr; $gaika</TD></TR>\r\n";


		if ($zavod_diskov != "") {
			echo "<TR><TD><center>заводская комплектация</center></TD></TR>\r\n";
			$zavod_diskov_ = explode('|',$zavod_diskov);
			for ($j=0; $j<count($zavod_diskov_); $j++) {
				$zavod_diskov__ = explode('#',$zavod_diskov_[$j]);
					if (count($zavod_diskov__) >= 2 ) {
						echo "<TR><TD>передняя ось: " . $zavod_diskov__[0] . " задняя ось: " . $zavod_diskov__[1] . "</TD></TR>\r\n";
					} else {
						echo "<TR><TD>" . $zavod_diskov_[$j] . "</TD></TR>\r\n";
					}
			}
		#echo "<br><br>\r\n";
		}



		if ($zamen_diskov != "") {
			echo "<TR><TD><center>варианты замены</center></TD></TR>\r\n";
			$zamen_diskov_ = explode('|',$zamen_diskov);
			for ($j=0; $j<count($zamen_diskov_); $j++) {
				$zamen_diskov__ = explode('#',$zamen_diskov_[$j]);
					if (count($zamen_diskov__) >= 2 ) {
						echo "<TR><TD>передняя ось: " . $zamen_diskov__[0] . " задняя ось: " . $zamen_diskov__[1] . "</TD></TR>\r\n";
					} else {
						echo "<TR><TD>" . $zamen_diskov_[$j] . "</TD></TR>\r\n";
					}
			}
		#echo "<br><br>\r\n";
		}



		if ($tuning_diski != "") {
			echo "<TR><TD><center>тюнинг</center></TD></TR>\r\n";
			$tuning_diski_ = explode('|',$tuning_diski);
			for ($j=0; $j<count($tuning_diski_); $j++) {
				$tuning_diski__ = explode('#',$tuning_diski_[$j]);
					if (count($tuning_diski__) >= 2 ) {
						echo "<TR><TD>передняя ось: " . $tuning_diski__[0] . " задняя ось: " . $tuning_diski__[1] . "</TD></TR>\r\n";
					} else {
						echo "<TR><TD>" . $tuning_diski_[$j] . "</TD></TR>\r\n";
					}
			}
		#echo "<br><br>\r\n";
		}

	}

	echo "</TABLE> \r\n";
                                                                                                                                                                                                                                                          
	exit;



}


if ($xajax == "getmodels") {
	header("Content-type: text/xml; charset=utf-8"); 
	
	$vendor_id = $xajaxargs[0];
	$result= SQL("SELECT * FROM `$db_name`.`$table_name` WHERE vendor = '" . addslashes($vendors[$vendor_id])."' ORDER BY `$table_name`.`car` ASC;") ;
	$i = 0;
	$out_ = "";
	$last_car = "";
	if(mysqli_num_rows($result))  { 
		while($row = mysqli_fetch_array($result)) {
			if ($last_car != $row['car']) {
				$i++;
				$out_ = $out_ . "<cmd n=\"as\" t=\"models\" p=\"options[$i].text\"><![CDATA[".$row['car']."]]></cmd>";
				$out_ = $out_ . "<cmd n=\"as\" t=\"models\" p=\"options[$i].value\"><![CDATA[".$row['id']."]]></cmd>";
				#$i++;
				$last_car = $row['car'];
			}
		}
	}

	$i++;
	$out_null = "<cmd n=\"as\" t=\"models\" p=\"options[0].text\"><![CDATA[Выберите марку]]></cmd>";
	$out_null = $out_null . "<cmd n=\"as\" t=\"models\" p=\"options[0].value\"><![CDATA[0]]></cmd>";


	$out__ =  "<cmd n=\"as\" t=\"modification\" p=\"options.length\"><![CDATA[0]]></cmd><cmd n=\"as\" t=\"modification\" p=\"options.length\"><![CDATA[0]]></cmd>";
	$out__ =  $out__ . "<cmd n=\"as\" t=\"year\" p=\"options.length\"><![CDATA[0]]></cmd><cmd n=\"as\" t=\"year\" p=\"options.length\"><![CDATA[0]]></cmd>";


	$out = "<?phpxml version=\"1.0\" encoding=\"utf-8\" ?><xjx><cmd n=\"as\" t=\"models\" p=\"options.length\"><![CDATA[0]]></cmd><cmd n=\"as\" t=\"models\" p=\"options.length\"><![CDATA[".$i."]]></cmd>";
	#echo iconv("windows-1251","utf-8",$out . $out__ . $out_null . $out_ . "</xjx>");
	echo $out . $out__ . $out_null . $out_ . "</xjx>";

	
}




if ($xajax == "getyear") {

	header("Content-type: text/xml; charset=utf-8"); 
	$year_id = $xajaxargs[0];

	if ($year_id == "") die("year_id is null in getyear");

	$result= SQL("SELECT * FROM `$db_name`.`$table_name` WHERE id = '" . addslashes($year_id) . "';") ;
	if(mysqli_num_rows($result))  { 
		$row = mysqli_fetch_array($result);
		$_vendor = $row['vendor'];
		$_car = $row['car'];
		#$_year = $row['year'];
	}



	$result= SQL("SELECT * FROM `$db_name`.`$table_name` WHERE vendor = '$_vendor' AND car = '$_car' ORDER BY `$table_name`.`year` ASC;") ;
	$i = 0;
	$out_ = "";
	$last_year = "";
	if(mysqli_num_rows($result))  { 
		while($row = mysqli_fetch_array($result)) {
			if ($last_year != $row['year']) {
				$i++;
				$out_ = $out_ . "<cmd n=\"as\" t=\"year\" p=\"options[$i].text\"><![CDATA[".$row['year']."]]></cmd>";
				$out_ = $out_ . "<cmd n=\"as\" t=\"year\" p=\"options[$i].value\"><![CDATA[".$row['id']."]]></cmd>";
				#$i++;
				$last_year = $row['year'];
			}
		}
	}
	
	$i++;
	$out_null =  "<cmd n=\"as\" t=\"year\" p=\"options[0].text\"><![CDATA[Выберите год выпуска]]></cmd>";
	$out_null = $out_null . "<cmd n=\"as\" t=\"year\" p=\"options[0].value\"><![CDATA[0]]></cmd>";


	$out__ =  "<cmd n=\"as\" t=\"modification\" p=\"options.length\"><![CDATA[0]]></cmd><cmd n=\"as\" t=\"modification\" p=\"options.length\"><![CDATA[0]]></cmd>";

	$out = "<?phpxml version=\"1.0\" encoding=\"utf-8\" ?><xjx><cmd n=\"as\" t=\"year\" p=\"options.length\"><![CDATA[0]]></cmd><cmd n=\"as\" t=\"year\" p=\"options.length\"><![CDATA[".$i."]]></cmd>";
	#echo iconv("windows-1251","utf-8",$out . $out__ . $out_null . $out_ . "</xjx>");
	echo $out . $out__ . $out_null . $out_ . "</xjx>";

}









if ($xajax == "getmodification") {

	header("Content-type: text/xml; charset=utf-8"); 

	$modification_id = $xajaxargs[0];
	$year_id = $xajaxargs[0];
	$out_ = "";

	if ($modification_id == "") die("modification_id is null in getmodification");


	$result= SQL("SELECT * FROM `$db_name`.`$table_name` WHERE id = '" . addslashes($modification_id) . "';") ;
	if(mysqli_num_rows($result))  { 
		$row = mysqli_fetch_array($result);
		$_vendor = $row['vendor'];
		$_car = $row['car'];
		$_year = $row['year'];
	}

	$result2= SQL("SELECT * FROM `$db_name`.`$table_name` WHERE vendor = '$_vendor' AND car = '$_car' AND year = '$_year'");


		#$result2 = SQL("SELECT * FROM `$db_name`.`$table_name` WHERE vendor = '$vendor' AND modification = '$modification';");
		$last_name = "";
		$i = 0;
		if(mysqli_num_rows($result2))  { 
			while($row2 = mysqli_fetch_array($result2)) {
				
				if ($last_name != $row2['modification']) {
					$last_name = $row2['modification'];


					#echo "<a href=\"?model_id=".$row2['id']. "\">".$row2['vendor'] . " -> ". $row2['modification']. " -> ". $row2['name'] . "</a><br>\r\n";
	
					$out_ = $out_ . "<cmd n=\"as\" t=\"modification\" p=\"options[$i].text\"><![CDATA[".$row2['modification']."]]></cmd>";
					$out_ = $out_ . "<cmd n=\"as\" t=\"modification\" p=\"options[$i].value\"><![CDATA[".$row2['id']."]]></cmd>";
					$i++;
		
				}

			}
		}

			


	$out =  "<?phpxml version=\"1.0\" encoding=\"utf-8\" ?><xjx><cmd n=\"as\" t=\"modification\" p=\"options.length\"><![CDATA[0]]></cmd><cmd n=\"as\" t=\"modification\" p=\"options.length\"><![CDATA[".$i."]]></cmd>";
	#echo iconv("windows-1251","utf-8",$out . $out_ . "</xjx>");
	echo $out . $out_ . "</xjx>";
	
}



?>





