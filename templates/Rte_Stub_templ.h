"""
typedef struct rteStubs_t 
{
	#for $func in $funcs_decl
	$for $val in $func["params"]["vals"]
	$val["type"] rteStubs.$func["name"]_$val["name"];
	#end for
	#end for
}

extern struct rteStubs_t rteStubs;
"""