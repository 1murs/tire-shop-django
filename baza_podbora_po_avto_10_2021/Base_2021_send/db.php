<?php
error_reporting(E_ALL);
ini_set("display_errors","1");
ini_set("error_reporting", E_ALL);


$db_host     = "127.0.0.1";
$db_user     = "root";
$db_password = "";
$db_name     = 'test_podbor';
$table_name     = 'podbor_shini_i_diski';



function SQL($query) {
   global $db_host, $db_user, $db_password, $db_name, $dbh;
   if (! $dbh) {
      $dbh = mysqli_connect($db_host, $db_user, $db_password, $db_name);
      //mysql_select_db($db_name);
   }
   mysqli_set_charset($dbh, 'utf8'); //mysql_query ("SET NAMES utf8"); 
   
   $sth = mysqli_query($dbh,$query); #mysql_query $db_name
   if (mysqli_errno($dbh)>0) {

		echo(mysqli_errno($dbh)." : ".mysqli_error($dbh)."<BR>\r\n $query<br>");
		die("Error in sql");
		exit;

   }

   return $sth;
}
?>