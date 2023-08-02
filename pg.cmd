@echo off
Rem With no parameters CD to %Playground%
Rem Otherwise supply the name of an environment variable to CD to, like HOMEPATH
SetLocal EnableDelayedExpansion
%HOMEDRIVE%
set newfolder=!%1!
if "%newfolder%"=="" set newfolder=!%playground%!
cd %newfolder%
EndLocal & set newfolder=%newfolder%
cd %newfolder%
set newfolder=
