
typedef struct rteStubs_t 
{
	#set $types = []
	#for $func in $funcs_decl
	#for $val in $func["params"]["vals"]
	<% type = func["name"] + '_' + val["name"] %>
	#if $type not in $types
	$val["type_basic"] $type;
	$types.append($type)
	#end if
	#end for
	#end for
}

extern struct rteStubs_t rteStubs;

