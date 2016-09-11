<?php

$prefix = "/home/shhdup/hat/";
$word_count = 50;

if (!isset($_POST["first_name"]) || !strlen($_POST["first_name"])) {
  die("Not enough arguments");
}
if (!isset($_POST["second_name"]) || !strlen($_POST["second_name"])) {
  die("Not enough arguments");
}
if (!isset($_POST["words"])) {
  die("Not enough arguments");
}

$files = count(scandir($prefix."/all"));

if ($files > 2000) {
  die('Too many files');
}

$all = "=====\n";
$all .= $_POST["first_name"]."\n";
$all .= $_POST["second_name"]."\n";
$all .= "===\n".$_POST["words"]."\n";

$full = fopen($prefix."/full.txt", "a");
fwrite($full, "\n".$all."\n");
fclose($full);

$extra = fopen($prefix."/all/".strval($files - 1).".txt", "w");
fwrite($extra, $all);
fclose($extra);

?>
