#raw
#include "Std_Types.h"
#include "Rte_Type.h"
#end raw

typedef struct 
{
	#set $types = []
	#for $func in $funcs_decl
	#for $val in $func["params"]["vals"]
<% type = func["name"] + '_' + val["name"] %>#slurp
	#if $type not in $types
	$val["type_basic"] $type;
$types.append($type) #slurp
	#end if
	#end for
	#end for
} rteStubs_t;


