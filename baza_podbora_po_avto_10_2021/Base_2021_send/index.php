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


                                                                                                                                                                                                                                                                

?>


<h3>Подбор шин и дисков по авто</h3>

<script type="text/javascript">

var xajaxRequestUri="2.php";
var xajaxDebug=false;
var xajaxStatusMessages=false;
var xajaxWaitCursor=true;
var xajaxDefinedGet=0;
var xajaxDefinedPost=1;
var xajaxLoaded=false;
function xajax_getmodels(){return xajax.call("getmodels", arguments, 1);}
function xajax_getmodification(){return xajax.call("getmodification", arguments, 1)    ;}    
function xajax_getyear(){return xajax.call("getyear", arguments, 1);}

function xajax_list(){return xajax.call("list", arguments, 1);}


</script>



<script type="text/javascript" src="xajax.js"></script>


<script type="text/javascript">
window.setTimeout(function () { if (!xajaxLoaded) { alert('Error: the xajax Javascript file could not be included. Perhaps the URL is incorrect?\nURL: http://192.168.1.2/podbor_shini_diski/xajax.js'); } }, 6000);
</script>


<form action='2.php' method="POST">
<input type=hidden name=show value='OK'>

Производитель:<br>
<select name=auto id=auto size=1 onchange="xajax_getmodels(this.value)" style="width:200px">
<option value="0">Выберите производителя</option>

<?php
	for ($j=0; $j<=count($vendors); $j++) {
		if ($vendors[$j] != "") {
			echo "<option value=\"$j\">".$vendors[$j]."</option>\r\n";
		}
	}
?>

</select><br/>

Марка:<br>
<select name=models id=models size=1  onchange="xajax_getyear(this.value)"  style="width:200px">
</select><br/>   

Год выпуска:<br>
<select name=year id=year  size=1 onchange="xajax_getmodification(this.value)"  style="width:200px">
</select><br/>

Модификация:<br>
<select name=modification id=modification  size=1  style="width:200px">
</select>



<br/>
<br/><input type="submit" value="Выбрать *">

<br/>* для подбора необходимо выбрать <b>все</b> параметры

</form>		
