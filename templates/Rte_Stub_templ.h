#raw
#include "Std_Types.h"
#include "Rte_Type.h"
#end raw

typedef struct 
{
	#set $types = []
	#for $func in $funcs_decl
	#for $val in $func["params"]["vals"]
	#if func["common_name"] == ''
<% type = func["name"] + '_' + val["name"] %>#slurp
	#else
<% type = func["common_name"] + '_' + val["name"] %>#slurp
	#end if
	#if $type not in $types
<% psize = '[' + str(len(func["defval"])) + ']' %>#slurp
	#if len($func["defval"]) < 2
	$val["type_basic"] $type;
	#else
	$val["type_basic"] $type$psize;
	#end if
$types.append($type) #slurp
	#end if
	#end for
	#end for
} rteStubs_t;


